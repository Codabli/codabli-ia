"""generate_image.py

Outil de génération d'images à partir d'une description textuelle.
"""

import os
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from langchain.tools import BaseTool, tool


def _request_image(prompt: str) -> bytes:
    """
    Appelle l'API de génération d'images OVH AI Endpoints.

    Parameters
    ----------
    prompt : str
        Description textuelle de l'image à générer.

    Returns
    -------
    bytes
        Contenu binaire de l'image générée.
    """
    load_dotenv()

    token = os.getenv("OVH_AI_ENDPOINTS_ACCESS_TOKEN")
    endpoint = os.getenv("OVH_AI_ENDPOINTS_IMAGE_URL")

    if not token or not endpoint:
        raise RuntimeError(
            "OVH_AI_ENDPOINTS_ACCESS_TOKEN et OVH_AI_ENDPOINTS_IMAGE_URL doivent être définies."
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


def create_image_generation_tool(output_dir: Path = Path("data/generated")) -> BaseTool:
    """
    Crée un outil de génération d'images utilisable par le LLM.

    Parameters
    ----------
    output_dir : pathlib.Path, default Path("data/generated")
        Dossier de stockage des images générées.

    Returns
    -------
    langchain.tools.BaseTool
        Outil LangChain de génération d'images.
    """

    @tool
    def generate_image(prompt: str) -> dict[str, str]:
        """
        Génère une nouvelle image à partir d'une description textuelle.

        Utiliser cet outil lorsque l'utilisateur demande explicitement
        de créer, générer ou illustrer une image.

        Args:
            prompt: Description textuelle du contenu visuel à générer.

        Returns:
            Dictionnaire contenant le prompt utilisé et le chemin du fichier généré.
        """
        image_bytes = _request_image(prompt)

        output_dir.mkdir(parents=True, exist_ok=True)

        # Nom unique pour éviter les écrasements
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        image_path = output_dir / f"{timestamp}.png"
        image_path.write_bytes(image_bytes)

        return {
            "prompt": prompt,
            "path": str(image_path.resolve()),
        }

    return generate_image
