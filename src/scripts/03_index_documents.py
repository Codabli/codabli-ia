"""03_index_documents.py

Script d'indexation des chunks dans un index vectoriel.

Commande
---------
python src/scripts/03_index_documents.py

Arguments
---------
--batch-size : int, default=64
    Nombre de chunks traités par lot.
--collection : str, default="conte_danse"
    Nom de la collection Chroma.
--input : str, default="data/processed/chunks.jsonl"
    Fichier JSONL contenant les chunks.
--persist-dir : str, default="storage/chroma"
    Dossier de persistance Chroma.
"""

import argparse

from src.ingestion.chunking import load_chunks
from src.ingestion.indexing import create_vector_store
from src.scripts import LOGGER


def main() -> None:
    """
    Point d'entrée du script d'indexation des chunks.
    """
    parser = argparse.ArgumentParser(description="Création de l'index vectoriel Conte Dansé.")

    parser.add_argument(
        "--input",
        default="data/processed/chunks.jsonl",
        help="Fichier JSONL contenant les chunks.",
    )
    parser.add_argument(
        "--persist-dir",
        default="storage/chroma",
        help="Dossier de persistance Chroma.",
    )
    parser.add_argument(
        "--collection",
        default="conte_danse",
        help="Nom de la collection Chroma.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Nombre de chunks traités par lot.",
    )

    args = parser.parse_args()

    LOGGER.info("1. Chargement des chunks...")
    chunks = load_chunks(args.input)
    LOGGER.info("   %s chunks chargés.", len(chunks))

    stores = create_vector_store(
        documents=chunks,
        persist_directory=args.persist_dir,
        collection_name=args.collection,
        batch_size=args.batch_size,
        rebuild=True,
    )

    LOGGER.info("2. Vérification de l'index...")
    for media_type, store in stores.items():
        LOGGER.info(
            "Collection %s : %s vecteurs",
            media_type,
            store._collection.count(),
        )

    LOGGER.info("Indexation terminée.")


if __name__ == "__main__":
    main()
