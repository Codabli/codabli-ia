"""test_generation.py

Tests pour le module de generation de réponses.
"""

from langchain_core.tools import tool
from src.generation.llm import create_llm


@tool
def search_images(query: str) -> str:
    """Recherche des images correspondant à une description."""
    return f"Recherche effectuée pour : {query}"


def test_tool_calling() -> None:
    """Test l'appel d'outil."""
    llm = create_llm()

    llm_with_tools = llm.bind_tools([search_images])

    response = llm_with_tools.invoke("Recherche des images de danseurs classiques.")

    assert response.tool_calls
    assert response.tool_calls[0]["name"] == "search_images"
