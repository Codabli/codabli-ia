"""indexing.py

Module de gestion de l'indexation des chunks dans Chroma.
"""

import hashlib
import json
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.ingestion.encoders import BaseEncoder, ImageEncoder, TextEncoder


def create_vector_store(
    documents: list[Document],
    persist_directory: str | Path = "storage/chroma",
    collection_name: str = "conte_danse",
    batch_size: int = 64,
    rebuild: bool = True,
) -> dict[str, Chroma]:
    """
    Crée ou met à jour les collections vectorielles Chroma à partir de documents.

    Cette fonction prend en charge deux types de médias : les textes et les images.
    Chaque type de média est indexé dans une collection Chroma distincte afin
    d'utiliser un encodeur adapté à la nature des données.

    Le traitement comprend plusieurs étapes :
    - Identification des types de médias présents dans les documents.
    - Initialisation des encodeurs nécessaires (TextEncoder et ImageEncoder).
    - Création des collections Chroma correspondantes.
    - Génération des embeddings par lots pour limiter l'utilisation de la mémoire.
    - Insertion ou mise à jour des documents et de leurs embeddings dans Chroma.

    Les documents textuels vides sont ignorés. Pour les images, le chemin du
    fichier est récupéré depuis les métadonnées du document.

    Les identifiants des chunks sont générés à partir de leur contenu et de
    leurs métadonnées afin de garantir leur unicité dans chaque collection.

    Parameters
    ----------
    documents : list[Document]
        Liste de documents à indexer.
    persist_directory : str | Path, default="storage/chroma"
        Répertoire où stocker l'index Chroma.
    collection_name : str, default="conte_danse"
        Nom de la collection Chroma.
    batch_size : int, default=64
        Nombre de documents à traiter par lot pour l'indexation.
    rebuild : bool, default=True
        Si True, supprime la collection existante avant de créer une nouvelle.

    Returns
    -------
    dict[str, Chroma]
        Dictionnaire contenant les instances des collections Chroma créées
        ou mises à jour.

        Les clés possibles sont :
        - "text" : collection contenant les embeddings textuels.
        - "image" : collection contenant les embeddings des images.

        Seuls les types de médias présents dans les documents sont retournés.

    Raises
    ------
    ValueError
        Si 'batch_size' est inférieur ou égal à zéro.
        Si plusieurs documents d'un même type de média possèdent le même
        identifiant de chunk.
    KeyError
        Si les métadonnées d'un document image ne contiennent pas la clé
        'file_path'.
    """
    if batch_size <= 0:
        raise ValueError("batch_size doit être strictement positif.")

    persist_path = Path(persist_directory)
    persist_path.mkdir(parents=True, exist_ok=True)

    collection_names = {
        "text": f"{collection_name}_text",
        "image": f"{collection_name}_image",
    }

    # Ne charger que les encodeurs nécessaires.
    encoders: dict[str, BaseEncoder] = {}
    for media_type in ("text", "image"):
        if any(
            document.metadata.get("media_type", "text") == media_type
            and (media_type == "image" or bool(document.page_content.strip()))
            for document in documents
        ):
            if media_type == "text":
                encoders[media_type] = TextEncoder(device="cpu")
            else:
                encoders[media_type] = ImageEncoder(device="cpu")

    stores = {}

    for media_type, encoder in encoders.items():
        collection = collection_names[media_type]

        media_documents = [
            document
            for document in documents
            if document.metadata.get("media_type", "text") == media_type
            and (media_type == "image" or bool(document.page_content.strip()))
        ]

        ids = [make_chunk_id(document) for document in media_documents]

        if len(ids) != len(set(ids)):
            raise ValueError(f"Des identifiants sont dupliqués dans les médias : {media_type}")

        if rebuild:
            existing = Chroma(
                collection_name=collection,
                persist_directory=str(persist_path),
            )
            existing.delete_collection()

        store = Chroma(
            collection_name=collection,
            persist_directory=str(persist_path),
            embedding_function=None,
            collection_metadata={"hnsw:space": "cosine"},
        )

        for start in range(0, len(media_documents), batch_size):
            batch = media_documents[start : start + batch_size]
            batch_ids = ids[start : start + batch_size]

            if media_type == "text":
                contents = [document.page_content for document in batch]
                embeddings = encoder.encode(contents)
            else:
                paths = [document.metadata["file_path"] for document in batch]
                embeddings = encoder.encode(paths)
                contents = [
                    document.page_content or document.metadata.get("filename", path)
                    for document, path in zip(batch, paths)
                ]

            store._collection.upsert(
                ids=batch_ids,
                embeddings=embeddings.tolist(),
                documents=contents,
                metadatas=[document.metadata for document in batch],
            )

        stores[media_type] = store

    return stores


def make_chunk_id(document: Document) -> str:
    """
    Crée un identifiant déterministe à partir du contenu et de la source.

    Parameters
    ----------
    document : Document
        Document dont on veut générer l'identifiant.

    Returns
    -------
    str
        Identifiant unique pour le chunk.
    """
    identity = {
        "source": document.metadata.get("source", ""),
        "page": document.metadata.get("page", ""),
        "start_index": document.metadata.get("start_index", ""),
        "file_path": document.metadata.get("file_path", ""),
        "content": document.page_content,
    }

    serialized = json.dumps(
        identity,
        sort_keys=True,
        ensure_ascii=False,
    )

    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
