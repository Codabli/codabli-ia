"""llm.py

Module de génération de texte à l'aide d'un modèle de langage hébergé par OVHcloud AI Endpoints.
"""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


def create_llm() -> ChatOpenAI:
    """
    Initialise le modèle hébergé par OVHcloud AI Endpoints.

    Returns
    -------
    ChatOpenAI
        Instance du modèle de langage Open AI.

    Raises
    ------
    RuntimeError
        Si les variables d'environnement nécessaires ne sont pas définies.
    """

    load_dotenv()

    api_key = os.getenv("OVH_AI_ENDPOINTS_ACCESS_TOKEN")
    model_name = os.getenv("OVH_AI_ENDPOINTS_MODEL_NAME")
    endpoint = os.getenv("OVH_AI_ENDPOINTS_URL")

    missing = [
        name
        for name, value in {
            "OVH_AI_ENDPOINTS_ACCESS_TOKEN": api_key,
            "OVH_AI_ENDPOINTS_MODEL_NAME": model_name,
            "OVH_AI_ENDPOINTS_URL": endpoint,
        }.items()
        if not value
    ]

    if missing:
        raise RuntimeError("Variables d'environnement manquantes : " + ", ".join(missing))

    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=endpoint,
        temperature=0.2,
        max_tokens=1200,
    )
