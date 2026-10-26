"""04_search.py

Script de recherche de passages dans l'index documentaire.

Commande
--------
python src/scripts/04_search.py "Votre question ici"

Arguments
---------
question : str
    Question à rechercher dans les documents.
-k : int, default=4
    Nombre de passages à retourner (défaut : 4).
"""

import argparse

from src.retrieval.retriever import load_vector_store, search_documents
from src.scripts import LOGGER


def main() -> None:
    """
    Point d'entrée du script de recherche de passages dans l'index documentaire.
    """
    parser = argparse.ArgumentParser(
        description="Recherche des passages dans l'index documentaire."
    )
    parser.add_argument(
        "question",
        help="Question à rechercher dans les documents.",
    )
    parser.add_argument(
        "-k",
        type=int,
        default=4,
        help="Nombre de passages à retourner (défaut : 4).",
    )
    args = parser.parse_args()

    vector_store = load_vector_store()
    results = search_documents(
        query=args.question,
        vector_store=vector_store,
        k=args.k,
    )

    LOGGER.info("\nQuestion : %s", args.question)
    LOGGER.info("Nombre de résultats : %s", len(results))

    for index, result in enumerate(results, start=1):
        metadata = result["metadata"]

        LOGGER.info("\n%s", "=" * 60)
        LOGGER.info("Résultat %s", index)
        LOGGER.info("Source : %s", metadata.get("source", "Inconnue"))
        LOGGER.info("Page : %s", metadata.get("page", "Non renseignée"))
        LOGGER.info("Distance : %.4f", result["distance"])
        LOGGER.info("\nExtrait :\n%s", result["content"][:1200])

        LOGGER.info("\n")
        LOGGER.info("\n%s", "-" * 60)


if __name__ == "__main__":
    main()
