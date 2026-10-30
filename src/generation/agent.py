"""agent.py

Configuration de l'assistant et de ses outils.
"""

from langchain_chroma import Chroma

from src.tools.image_generation import create_image_generation_tool
from src.tools.image_search import create_image_search_tool


def create_assistant_tools(vector_stores: dict[str, Chroma]) -> list:
    """
    Initialise les outils disponibles pour l'assistant.

    Parameters
    ----------
    vector_stores : dict
        Vector stores déjà chargés, partagés avec le reste de la chaîne.

    Returns
    -------
    list
        Liste des outils utilisables par le LLM.
    """

    return [
        create_image_search_tool(vector_stores),
        create_image_generation_tool(),
    ]
