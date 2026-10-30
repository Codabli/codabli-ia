"""chain.py

Gestion de l'assistant et de ses interactions avec les outils.
"""

import json

from langchain.tools import BaseTool
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from src.constants import MAX_EXECUTION_CYCLES_AGENT
from src.generation.agent import create_assistant_tools
from src.generation.llm import create_llm
from src.generation.prompt import SYSTEM_PROMPT
from src.retrieval.retriever import load_vector_stores, search_documents


def _format_context(results: list[dict]) -> tuple[str, list[dict]]:
    """
    Formate les passages en extraits identifiables et citables.

    Parameters
    ----------
    results : list[dict]
        Liste de dictionnaires contenant le contenu, les métadonnées et la distance pour chaque
        passage le plus proche de la question.

    Returns
    -------
    tuple[str, list[dict]]
        Une chaîne de caractères représentant le contexte formaté et une liste de dictionnaires
        contenant les informations sur les sources.
    """

    if not results:
        return "Aucun extrait pertinent trouvé dans les documents.", []

    blocks = []
    sources = []

    for index, result in enumerate(results, start=1):
        source_id = f"S{index}"
        metadata = result["metadata"]

        source = {
            "id": source_id,
            "source": metadata.get("source", "Source inconnue"),
            "page": metadata.get("page"),
            "distance": result["distance"],
        }
        sources.append(source)

        blocks.append(
            f"[{source_id}]\n"
            f"Fichier : {source['source']}\n"
            f"Page : {source['page']}\n"
            f"Contenu :\n{result['content']}"
        )

    return "\n\n---\n\n".join(blocks), sources


def create_assistant(vector_stores: dict[str, Chroma]) -> BaseTool:
    """
    Initialise le LLM et les outils disponibles.

    Parameters
    ----------
    vector_stores : dict
        Vector stores déjà chargés.

    Returns
    -------
    BaseTool
        LLM configuré avec ses outils et dictionnaire des outils.
    """

    llm = create_llm()
    tools = create_assistant_tools(vector_stores)

    tools_by_name = {tool.name: tool for tool in tools}
    llm_with_tools = llm.bind_tools(tools)

    return llm_with_tools, tools_by_name


def run_assistant(question: str, k: int = 3) -> dict:
    """
    Exécute une conversation avec l'assistant.

    Les extraits documentaires pertinents sont récupérés avant l'appel au LLM
    et injectés dans le prompt système. Le LLM peut ensuite répondre
    directement ou appeler un ou plusieurs outils.

    Parameters
    ----------
    question : str
        Question de l'utilisateur.
    k : int, default=3
        Nombre d'extraits documentaires récupérés.

    Returns
    -------
    dict
        Question, réponse, résultats des outils, sources documentaires et
        consommation de tokens cumulée.
    """
    if not question or not question.strip():
        raise ValueError("La question ne doit pas être vide.")

    question = question.strip()

    # Chargement unique des vector stores
    vector_stores = load_vector_stores()

    # Récupération du contexte documentaire (RAG)
    results = search_documents(
        query=question,
        vector_stores=vector_stores,
        k=k,
        media_types=["text"],
    )
    context, sources = _format_context(results)

    llm, tools = create_assistant(vector_stores)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT.format(context=context)),
        HumanMessage(content=question),
    ]

    tool_results = []
    usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

    for _ in range(MAX_EXECUTION_CYCLES_AGENT):
        response = llm.invoke(messages)
        messages.append(response)

        # Cumul des tokens sur tous les appels du LLM
        response_usage = response.usage_metadata or {}
        for key in usage:
            usage[key] += response_usage.get(key, 0)

        # Aucun outil demandé : le LLM a terminé sa réponse.
        if not response.tool_calls:
            break

        # Exécuter les outils demandés par le LLM.
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]

            if tool_name not in tools:
                raise ValueError(f"Outil inconnu : {tool_name}")

            result = tools[tool_name].invoke(tool_call["args"])

            tool_results.append({"tool": tool_name, "results": result})

            messages.append(
                ToolMessage(
                    content=json.dumps(result, ensure_ascii=False, default=str),
                    tool_call_id=tool_call["id"],
                    name=tool_name,
                )
            )

    else:
        raise RuntimeError("Nombre maximal d'itérations de l'assistant atteint.")

    return {
        "question": question,
        "answer": response.content,
        "tool_results": tool_results,
        "sources": sources,
        "usage": usage,
    }
