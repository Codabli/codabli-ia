"""01_ingest.py

Script d'ingestion des documents du RAG Conte Dansé.

Commande
--------
python src/scripts/01_ingest.py

Arguments
---------
--input : str, default="data/raw"
    Dossier contenant les documents source.
--output : str, default="data/processed/documents.jsonl"
    Fichier de sortie JSONL.
"""

import argparse
import json
from pathlib import Path

from src.ingestion.loaders import ingest_directory
from src.scripts import LOGGER


def main() -> None:
    """
    Point d'entrée du script d'ingestion.
    """
    parser = argparse.ArgumentParser(description="Ingestion des documents du RAG Conte Dansé.")
    parser.add_argument(
        "--input",
        default="data/raw",
        help="Dossier contenant les documents source.",
    )
    parser.add_argument(
        "--output",
        default="data/processed/documents.jsonl",
        help="Fichier de sortie JSONL.",
    )

    args = parser.parse_args()
    documents = ingest_directory(args.input)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Un objet JSON par ligne, pratique pour inspecter les résultats.
    with output_path.open("w", encoding="utf-8") as output_file:
        for document in documents:
            record = {
                "page_content": document.page_content,
                "metadata": document.metadata,
            }
            output_file.write(json.dumps(record, ensure_ascii=False) + "\n")

    LOGGER.info("Ingestion terminée : %s élément(s).", len(documents))
    LOGGER.info("Résultat enregistré dans : %s", output_path.resolve())


if __name__ == "__main__":
    main()
