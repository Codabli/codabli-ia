"""chain.py

Gestion de l'assistant et de ses interactions avec les outils.
"""

import json

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from src.generation.agent import create_assistant_tools
from src.generation.llm import create_llm
from src.generation.prompt import SYSTEM_PROMPT


def create_assistant():
    """
    Initialise le LLM et les outils disponibles.

    Returns
    -------
    tuple
        LLM configuré avec ses outils et dictionnaire des outils.
    """

    llm = create_llm()
    tools = create_assistant_tools()

    tools_by_name = {tool.name: tool for tool in tools}
    llm_with_tools = llm.bind_tools(tools)

    return llm_with_tools, tools_by_name


def run_assistant(question: str) -> dict:
    """
    Exécute une conversation avec l'assistant.

    Le LLM peut répondre directement ou appeler un ou plusieurs outils.

    Parameters
    ----------
    question : str
        Question de l'utilisateur.

    Returns
    -------
    dict
        Réponse de l'assistant et résultats des outils utilisés.
    """

    if not question or not question.strip():
        raise ValueError("La question ne doit pas être vide.")

    llm, tools = create_assistant()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question.strip()),
    ]

    tool_results = []

    max_iterations = 5

    for _ in range(max_iterations):
        response = llm.invoke(messages)

        messages.append(response)

        # Aucun outil demandé : le LLM a terminé sa réponse.
        if not response.tool_calls:
            break

        # Exécuter les outils demandés par le LLM.
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]

            if tool_name not in tools:
                raise ValueError(f"Outil inconnu : {tool_name}")

            tool = tools[tool_name]

            result = tool.invoke(tool_call["args"])

            tool_results.append(
                {
                    "tool": tool_name,
                    "results": result,
                }
            )

            messages.append(
                ToolMessage(
                    content=json.dumps(result, ensure_ascii=False),
                    tool_call_id=tool_call["id"],
                )
            )

    else:
        raise RuntimeError("Nombre maximal d'itérations de l'assistant atteint.")

    return {
        "question": question,
        "answer": response.content,
        "tool_results": tool_results,
    }
