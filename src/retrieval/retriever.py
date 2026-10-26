"""retriever.py

Module de recherche de documents dans un index vectoriel.
"""

from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from src.ingestion.indexing import DEFAULT_EMBEDDING_MODEL


def load_vector_store(
    persist_directory: str = "storage/chroma",
    collection_name: str = "conte_danse",
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
) -> Chroma:
    """
    Charge l'index Chroma existant, sans le reconstruire.

    Parameters
    ----------
    persist_directory : str, default="storage/chroma"
        Répertoire où l'index Chroma est stocké.
    collection_name : str, default="conte_danse"
        Nom de la collection Chroma à charger.
    embedding_model : str, default=DEFAULT_EMBEDDING_MODEL
        Nom du modèle d'embeddings à utiliser pour la recherche.

    Returns
    -------
    Chroma
        Instance de la collection Chroma chargée.

    Raises
    ------
    FileNotFoundError
        Si le répertoire de l'index n'existe pas.
    ValueError
        Si la collection est vide.
    """

    persist_path = Path(persist_directory)

    if not persist_path.exists():
        raise FileNotFoundError(
            f"Index introuvable : {persist_path}. Lancez d'abord scripts/index_documents.py."
        )

    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(persist_path),
    )

    if vector_store._collection.count() == 0:
        raise ValueError(f"La collection '{collection_name}' ne contient aucun passage.")

    return vector_store


def search_documents(query: str, vector_store: Chroma, k: int = 4) -> list[dict]:
    """
    Retourne les k passages les plus proches de la question.

    Parameters
    ----------
    query : str
        Question posée par l'utilisateur.
    vector_store : Chroma
        Instance de la collection Chroma à interroger.
    k : int, default=4
        Nombre de passages à retourner.

    Returns
    -------
    list[dict]
        Liste de dictionnaires contenant le contenu, les métadonnées et la distance pour chaque
        passage le plus proche de la question.

    Raises
    ------
    ValueError
        Si la question est vide ou si k est inférieur à 1.
    """

    if not query or not query.strip():
        raise ValueError("La question ne doit pas être vide.")

    if k < 1:
        raise ValueError("Le paramètre k doit être supérieur ou égal à 1.")

    results = vector_store.similarity_search_with_score(
        query.strip(),
        k=k,
    )

    return [
        {
            "content": document.page_content,
            "metadata": document.metadata,
            "distance": float(distance),
        }
        for document, distance in results
    ]
