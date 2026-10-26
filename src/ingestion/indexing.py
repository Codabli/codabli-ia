"""indexing.py

Module de gestion de l'indexation des chunks dans Chroma.
"""

import hashlib
import json
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from src.constants import DEFAULT_EMBEDDING_MODEL


def create_vector_store(
    documents: list[Document],
    persist_directory: str | Path = "storage/chroma",
    collection_name: str = "conte_danse",
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    batch_size: int = 64,
    rebuild: bool = True,
) -> Chroma:
    """
    Calcule les embeddings et crée ou met à jour l'index Chroma.

    Parameters
    ----------
    documents : list[Document]
        Liste de documents à indexer.
    persist_directory : str | Path, default="storage/chroma"
        Répertoire où stocker l'index Chroma.
    collection_name : str, default="conte_danse"
        Nom de la collection Chroma.
    embedding_model : str, default=DEFAULT_EMBEDDING_MODEL
        Nom du modèle d'embeddings à utiliser.
    batch_size : int, default=64
        Nombre de documents à traiter par lot pour l'indexation.
    rebuild : bool, default=True
        Si True, supprime la collection existante avant de créer une nouvelle.

    Returns
    -------
    Chroma
        Instance de la collection Chroma créée ou mise à jour.

    Raises
    ------
    ValueError
        Si batch_size est inférieur ou égal à zéro.
    """
    if batch_size <= 0:
        raise ValueError("batch_size doit être strictement positif.")

    persist_path = Path(persist_directory)
    persist_path.mkdir(parents=True, exist_ok=True)

    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    if rebuild:
        # Reconstruction complète : évite de conserver des chunks supprimés
        # depuis le dernier index.
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=str(persist_path),
        )
        vector_store.delete_collection()

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(persist_path),
        collection_metadata={"hnsw:space": "cosine"},
    )

    ids = [make_chunk_id(document) for document in documents]

    if len(ids) != len(set(ids)):
        raise ValueError(
            "Des identifiants de chunks sont dupliqués. Vérifiez les sources, pages et positions "
            "des chunks."
        )

    # Chroma ne prend pas en charge tous les types de métadonnées.
    # Nous conservons les valeurs simples et ignorons les valeurs nulles.
    for document in documents:
        document.metadata = {
            key: value
            for key, value in document.metadata.items()
            if value is not None and isinstance(value, (str, int, float, bool))
        }

    for start in range(0, len(documents), batch_size):
        batch_documents = documents[start : start + batch_size]
        batch_ids = ids[start : start + batch_size]

        vector_store.add_documents(
            documents=batch_documents,
            ids=batch_ids,
        )

    return vector_store


def load_chunks(input_path: str | Path) -> list[Document]:
    """
    Recharge les chunks produits à l'étape précédente.

    Parameters
    ----------
    input_path : str | Path
        Chemin vers le fichier JSONL contenant les chunks.

    Returns
    -------
    list[Document]
        Liste de documents représentant les chunks.

    Raises
    ------
    FileNotFoundError
        Si le fichier de chunks n'existe pas.
    ValueError
        Si le fichier est vide ou contient des chunks invalides.
    """
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"Fichier de chunks introuvable : {path}")

    documents = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
                content = record["page_content"]
                metadata = record["metadata"]

                if not isinstance(content, str) or not content.strip():
                    continue

                if not isinstance(metadata, dict):
                    raise ValueError("Les métadonnées doivent être un objet.")

                documents.append(
                    Document(
                        page_content=content,
                        metadata=metadata,
                    )
                )

            except (json.JSONDecodeError, KeyError, ValueError) as exc:
                raise ValueError(f"Chunk invalide à la ligne {line_number}") from exc

    if not documents:
        raise ValueError("Aucun chunk exploitable trouvé.")

    return documents


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
        "content": document.page_content,
    }

    serialized = json.dumps(
        identity,
        sort_keys=True,
        ensure_ascii=False,
    )

    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
