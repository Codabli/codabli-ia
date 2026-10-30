"""llm.py

Module de génération de texte à l'aide d'un modèle de langage hébergé par OVHcloud AI Endpoints.
"""

import os
import requests
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI


def create_llm() -> ChatMistralAI:
    """
    Initialise le modèle hébergé par OVHcloud AI Endpoints.

    Returns
    -------
    ChatMistralAI
        Instance du modèle de langage Mistral.

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

    return ChatMistralAI(
        model=model_name,
        api_key=api_key,
        endpoint=endpoint,
        temperature=0.2,
        max_tokens=1200,
    )



def generate_image(prompt: str) -> bytes:
    load_dotenv()

    token = os.getenv("OVH_AI_ENDPOINTS_ACCESS_TOKEN")
    endpoint = os.getenv("OVH_AI_ENDPOINTS_IMAGE_URL")

    if not token or not endpoint:
        raise RuntimeError(
            "OVH_AI_ENDPOINTS_ACCESS_TOKEN et OVH_AI_ENDPOINTS_IMAGE_URL "
            "doivent être définies."
        )

    response = requests.post(
        endpoint,
        headers={"Authorization": f"Bearer {token}"},
        json={
            "model": "stable-diffusion-xl-base-v10",
            "prompt": prompt,
        },
        timeout=120,
    )
    response.raise_for_status()
    
    return response.content