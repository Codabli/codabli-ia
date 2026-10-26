"""02_chunk_documents.py

Script de découpage des documents en chunks.

Commande
---------
python src/scripts/02_chunk_documents.py

Arguments
---------
--input : str, default="data/raw"
    Fichier JSONL issu de l'ingestion (par défaut : data/processed/documents.jsonl)
--output : str, default="data/processed/chunks.jsonl"
    Fichier JSONL des chunks (par défaut : data/processed/chunks.jsonl)
--chunk-size : int, default=600
    Taille maximale d'un chunk (par défaut : 600 caractères)
--chunk-overlap : int, default=100
    Chevauchement entre les chunks (par défaut : 100 caractères)
"""

import argparse
import json
from pathlib import Path

from langchain_core.documents import Document

from src.ingestion.chunking import split_documents
from src.scripts import LOGGER


def main() -> None:
    """
    Point d'entrée du script de découpage des documents en chunks.
    """
    parser = argparse.ArgumentParser(description="Découpage des documents en chunks.")
    parser.add_argument(
        "--input",
        default="data/processed/documents.jsonl",
        help="Fichier JSONL issu de l'ingestion.",
    )
    parser.add_argument(
        "--output",
        default="data/processed/chunks.jsonl",
        help="Fichier JSONL des chunks.",
    )
    parser.add_argument("--chunk-size", type=int, default=600)
    parser.add_argument("--chunk-overlap", type=int, default=100)

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Fichier d'entrée introuvable : {input_path}")

    documents = []

    with input_path.open("r", encoding="utf-8") as input_file:
        for line_number, line in enumerate(input_file, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
                documents.append(
                    Document(
                        page_content=record["page_content"],
                        metadata=record["metadata"],
                    )
                )
            except (json.JSONDecodeError, KeyError) as exc:
                raise ValueError(f"Entrée invalide à la ligne {line_number}") from exc

    if not documents:
        raise ValueError("Aucun document exploitable dans le fichier.")

    chunks = split_documents(
        documents,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as output_file:
        for chunk in chunks:
            output_file.write(
                json.dumps(
                    {
                        "page_content": chunk.page_content,
                        "metadata": chunk.metadata,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    lengths = [len(chunk.page_content) for chunk in chunks]

    LOGGER.info("Documents d'entrée : %s", len(documents))
    LOGGER.info("Chunks créés : %s", len(chunks))
    LOGGER.info("Taille minimale : %s caractères", min(lengths))
    LOGGER.info("Taille maximale : %s caractères", max(lengths))
    LOGGER.info("Taille moyenne : %.1f caractères", sum(lengths) / len(lengths))
    LOGGER.info("Fichier de sortie : %s", output_path.resolve())


if __name__ == "__main__":
    main()
