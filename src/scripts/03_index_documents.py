"""03_index_documents.py

Script d'indexation des chunks dans un index vectoriel.

Commande
---------
python src/scripts/03_index_documents.py

Arguments
---------
--input : str, default="data/processed/chunks.jsonl"
    Fichier JSONL contenant les chunks.
--persist-dir : str, default="storage/chroma"
    Dossier de persistance Chroma.
--collection : str, default="conte_danse"
    Nom de la collection Chroma.
--embedding-model : str, default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    Nom du modèle d'embeddings.
--batch-size : int, default=64
    Nombre de chunks traités par lot.
"""

import argparse

from src.ingestion.indexing import create_vector_store, load_chunks
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
        "--embedding-model",
        default=("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"),
        help="Nom du modèle d'embeddings.",
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

    LOGGER.info("2. Création des embeddings et de l'index...")
    LOGGER.info("   Modèle : %s", args.embedding_model)

    vector_store = create_vector_store(
        documents=chunks,
        persist_directory=args.persist_dir,
        collection_name=args.collection,
        embedding_model=args.embedding_model,
        batch_size=args.batch_size,
        rebuild=True,
    )

    LOGGER.info("3. Vérification de l'index...")
    count = vector_store._collection.count()

    LOGGER.info("   Nombre de vecteurs : %s", count)
    LOGGER.info("   Dossier : %s", args.persist_dir)
    LOGGER.info("   Collection : %s", args.collection)
    LOGGER.info("Indexation terminée.")


if __name__ == "__main__":
    main()
