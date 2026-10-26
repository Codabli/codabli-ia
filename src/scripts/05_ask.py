"""05_ask.py

Script de question-réponse utilisant le RAG Conte Dansé.

Commande
--------
python src/scripts/05_ask.py "Votre question ici"

Arguments
---------
question : str
    Question à poser à l'assistant RAG.
-k : int, default=4
    Nombre de passages à retourner pour la génération de la réponse (défaut : 4).
"""

import argparse

from src.generation.rag_chain import answer_question
from src.scripts import LOGGER


def main() -> None:
    """
    Point d'entrée du script de question-réponse.
    """
    parser = argparse.ArgumentParser(description="Pose une question à l'assistant RAG.")
    parser.add_argument("question", help="Question à poser.")
    parser.add_argument("-k", type=int, default=4)
    args = parser.parse_args()

    result = answer_question(args.question, k=args.k)

    LOGGER.info("\nQUESTION\n%s", result["question"])

    LOGGER.info("\nRÉPONSE\n%s", result["answer"])

    LOGGER.info("\nSOURCES RETROUVÉES")
    for source in result["sources"]:
        LOGGER.info(
            "[%s] %s | page : %s | distance : %.4f",
            source["id"],
            source["source"],
            source["page"],
            source["distance"],
        )


if __name__ == "__main__":
    main()
