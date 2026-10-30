"""image_search.py

Outil de recherche d'images dans la banque documentaire.
"""

from typing import Any

from langchain.tools import BaseTool, tool

from src.retrieval.retriever import search_documents


def create_image_search_tool(vector_stores: dict[str, Any]) -> BaseTool:
    """
    Crée un outil de recherche d'images utilisable par le LLM.

    Parameters
    ----------
    vector_stores : dict of str to Any
        Collections vectorielles Chroma disponibles, indexées par nom.

    Returns
    -------
    langchain.tools.BaseTool
        Outil LangChain de recherche d'images.
    """

    @tool
    def search_images(query: str) -> list[dict[str, Any]]:
        """
        Recherche les images les plus pertinentes dans la banque d'images.

        Utiliser cet outil lorsque l'utilisateur demande explicitement
        à rechercher, retrouver ou afficher des images existantes.

        Args:
            query: Description textuelle du contenu visuel recherché.

        Returns:
            Liste des images trouvées avec leurs métadonnées et distances.
        """

        results = search_documents(
            query=query,
            vector_stores=vector_stores,
            k=5,
            media_types=["image"],
        )

        return [
            {
                "content": result["content"],
                "metadata": result["metadata"],
                "distance": result["distance"],
            }
            for result in results
        ]

    return search_images
