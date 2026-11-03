
"""
06_chat.py

Script de discussion utilisant l'assistant Conte Dansé.

Commande
--------
python -m src.scripts.06_chat
"""

from src.generation.chain import run_assistant
from src.utils.common import save_conversation
from src.scripts import LOGGER


def main():

    conversation = []

    all_tool_results = []
    all_sources = []

    LOGGER.info("Démarrage de la conversation avec l'assistant AI.")

    print("\nAssistant AI démarré.", flush=True)
    print("Tapez 'exit' ou 'quit' pour terminer la discussion.\n", flush=True)

    while True:

        try:
            question = input("Vous : ").strip()

            if question.lower() in ("exit", "quit"):
                break

            if not question:
                continue

            LOGGER.info("Question reçue : %s", question)

            result = run_assistant(question)

            answer = result["answer"]

            print(f"\nAssistant : {answer}\n", flush=True)

            conversation.extend([
                {
                    "role": "user",
                    "content": question,
                },
                {
                    "role": "assistant",
                    "content": answer,
                },
            ])

            all_tool_results.extend(result.get("tool_results", []))
            all_sources.extend(result.get("sources", []))

        except KeyboardInterrupt:
            print("\nInterruption de la conversation.")
            break

        except Exception:
            LOGGER.exception("Erreur durant la conversation.")
            print("Une erreur est survenue.")

    # Sauvegarde uniquement si la conversation contient des échanges
    if conversation:

        output_path = save_conversation(
            conversation=conversation,
            tool_results=all_tool_results,
            sources=all_sources,
        )

        LOGGER.info("Conversation enregistrée : %s", output_path)

        print(f"\nConversation sauvegardée dans : {output_path}")

    else:
        print("\nAucune conversation à sauvegarder.")


if __name__ == "__main__":
    main()
