"""chunking.py

Module de découpage de documents en chunks.
"""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(
    documents: list[Document], chunk_size: int = 600, chunk_overlap: int = 100
) -> list[Document]:
    """
    Découpe les documents en chunks en conservant leurs métadonnées.

    Parameters
    ----------
    documents : list[Document]
        Liste de documents à découper.
    chunk_size : int, default=600
        Taille maximale approximative en caractères pour chaque chunk.
    chunk_overlap : int, default=100
        Chevauchement entre les chunks en caractères.

    Returns
    -------
    list[Document]
        Liste de documents représentant les chunks.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size doit être strictement positif.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap ne peut pas être négatif.")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap doit être inférieur à chunk_size.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
        add_start_index=True,
    )

    chunks = splitter.split_documents(documents)

    # Ajoute un identifiant stable pour chaque position dans le lot.
    # Pour une indexation incrémentale, il faudra ensuite stabiliser
    # ces identifiants à partir du document et du contenu.
    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = f"chunk_{index:05d}"
        chunk.metadata["chunk_length"] = len(chunk.page_content)

    return chunks
