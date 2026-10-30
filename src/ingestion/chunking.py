"""chunking.py

Module de découpage de documents en chunks.
"""

import json
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_chunks(input_path: str | Path) -> list[Document]:
    """
    Charge les documents depuis un fichier JSONL.

    Conserve les images même si leur contenu textuel est vide et ignore
    les documents textuels dont le contenu est vide.
    """
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    documents = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
                content = record["page_content"]
                metadata = record["metadata"]

                if not isinstance(content, str):
                    raise ValueError("Le contenu doit être une chaîne de caractères.")

                if not isinstance(metadata, dict):
                    raise ValueError("Les métadonnées doivent être un objet.")

                media_type = metadata.get("media_type")

                if media_type == "text" and not content.strip():
                    continue

                documents.append(
                    Document(
                        page_content=content,
                        metadata=metadata,
                    )
                )

            except (json.JSONDecodeError, KeyError, ValueError) as exc:
                raise ValueError(f"Document invalide à la ligne {line_number} de {path}") from exc

    if not documents:
        raise ValueError(f"Aucun document exploitable trouvé dans {path}.")

    return documents


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

    empty_documents = [doc for doc in documents if not doc.page_content.strip()]
    chunks = splitter.split_documents(documents)
    chunks.extend(empty_documents)

    # Ajoute un identifiant stable pour chaque position dans le lot.
    # Pour une indexation incrémentale, il faudra ensuite stabiliser
    # ces identifiants à partir du document et du contenu.
    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = f"chunk_{index:05d}"
        chunk.metadata["chunk_length"] = len(chunk.page_content)

    return chunks
