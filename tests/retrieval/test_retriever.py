"""test_retriever.py

Tests pour le module de récupération de documents.
"""

import pytest
from src.retrieval.retriever import search_documents


def test_rejects_empty_question() -> None:
    """Teste que la fonction search_documents lève une exception pour une question vide."""
    with pytest.raises(ValueError):
        search_documents("", vector_store=None)


def test_rejects_invalid_k() -> None:
    """Teste que la fonction search_documents lève une exception pour un k invalide."""
    with pytest.raises(ValueError):
        search_documents("château fort", vector_store=None, k=0)


def test_rejects_whitespace_question() -> None:
    """
    Teste que la fonction search_documents lève une exception pour une question composée
    uniquement d'espaces.
    """
    with pytest.raises(ValueError):
        search_documents("   ", vector_store=None)
