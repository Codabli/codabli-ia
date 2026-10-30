"""02_chunk_documents.py

Script de découpage des documents en chunks.

Commande
---------
python src/scripts/02_chunk_documents.py

Arguments
---------
--chunk-overlap : int, default=100
    Nombre de caractères pour le chevauchement entre les chunks
--chunk-size : int, default=600
    Taille maximale de caractères d'un chunk
--input : str, default="data/processed/documents.jsonl"
    Fichier JSONL issu de l'ingestion
--output : str, default="data/processed/chunks.jsonl"
    Fichier JSONL des chunks
"""

import argparse
import json
from pathlib import Path

from src.ingestion.chunking import load_chunks, split_documents
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

    documents = load_chunks(input_path)

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
