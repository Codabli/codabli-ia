"""05_ask.py

Script de question-réponse utilisant l'assistant Conte Dansé.

Commande
--------
python src/scripts/05_ask.py "Votre question ici"

Arguments
---------
question : str
    Question à poser à l'assistant RAG.
"""

import argparse

from src.generation.chain import run_assistant
from src.scripts import LOGGER
from src.utils.common import save_output


def main():
    parser = argparse.ArgumentParser(description="Interroger l'assistant Conte Dansé.")

    parser.add_argument("question", type=str, help="Question à poser à l'assistant.")

    args = parser.parse_args()
    question = args.question

    LOGGER.info("Question reçue : %s", question)

    result = run_assistant(question)
    answer = result["answer"]

    output_path = save_output(
        question=question,
        answer=answer,
        tool_results=result["tool_results"],
        sources=result["sources"],
    )

    LOGGER.info("Résultats enregistrés dans : %s", output_path)
    LOGGER.info("Réponse : %s", answer)


if __name__ == "__main__":
    main()
