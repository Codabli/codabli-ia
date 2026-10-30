"""agent.py

Configuration de l'assistant et de ses outils.
"""

from src.retrieval.retriever import load_vector_stores
from src.tools.image_search import create_image_search_tool


def create_assistant_tools():
    """
    Initialise les outils disponibles pour l'assistant.

    Returns
    -------
    list
        Liste des outils utilisables par le LLM.
    """

    vector_stores = load_vector_stores()
    image_search_tool = create_image_search_tool(vector_stores)

    return [
        image_search_tool,
    ]
