"""encoders/image.py

Module d'encodage des images et des requêtes textuelles pour la recherche
texte-vers-image.
"""

from pathlib import Path
from typing import Sequence

import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer

from src.constants import EMBEDDING_MODEL_IMG, EMBEDDING_MODEL_TXT_TO_IMG
from src.ingestion.encoders.base import BaseEncoder


class ImageEncoder(BaseEncoder):
    """
    Encode les images et les requêtes textuelles pour la recherche
    texte-vers-image.

    Cette classe utilise deux modèles SentenceTransformer :
    - Un modèle pour encoder les images.
    - Un modèle pour encoder les requêtes textuelles.

    Les deux modèles produisent des embeddings dans un espace vectoriel
    commun, permettant de comparer les images et les requêtes textuelles.

    Parameters
    ----------
    device : str, default="cpu"
        Périphérique utilisé pour l'exécution des modèles
        (par exemple, "cpu" ou "cuda").

    Attributes
    ----------
    image_model : SentenceTransformer
        Modèle chargé de l'encodage des images.

    query_model : SentenceTransformer
        Modèle chargé de l'encodage des requêtes textuelles.
    """

    def __init__(self, device: str = "cpu") -> None:
        # Encodeur des images
        self.image_model = SentenceTransformer(EMBEDDING_MODEL_IMG, device=device)

        # Encodeur des requêtes textuelles compatibles avec les images
        self.query_model = SentenceTransformer(EMBEDDING_MODEL_TXT_TO_IMG, device=device)

    def encode(self, inputs: Sequence[str | Path]) -> np.ndarray:
        """
        Encode une séquence de chemins d'images en embeddings.

        Les images sont ouvertes, converties au format RGB, puis encodées
        par le modèle visuel. Les embeddings obtenus sont normalisés.

        Parameters
        ----------
        inputs : Sequence[str | Path]
            Séquence de chemins vers les images à encoder.

        Returns
        -------
        np.ndarray
            Tableau NumPy de type float32 contenant les embeddings
            normalisés des images. Sa forme est (n_images, 512).

            Si la séquence est vide, retourne un tableau vide de forme
            (0, 512).
        """

        if not inputs:
            return np.empty((0, 512), dtype=np.float32)

        images = []

        for path in inputs:
            with Image.open(path) as image:
                images.append(image.convert("RGB").copy())

        embeddings = self.image_model.encode(
            images,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return embeddings.astype(np.float32)

    def encode_queries(self, queries: Sequence[str]) -> np.ndarray:
        """
        Encode des requêtes textuelles dans l'espace vectoriel des images.

        Les requêtes sont encodées par le modèle textuel compatible avec
        la recherche texte-vers-image. Les embeddings obtenus sont
        normalisés.

        Parameters
        ----------
        queries : Sequence[str]
            Séquence de requêtes textuelles à encoder.

        Returns
        -------
        np.ndarray
            Tableau NumPy de type float32 contenant les embeddings
            normalisés des requêtes. Sa forme est (n_requêtes, 512).

            Si la séquence est vide, retourne un tableau vide de forme
            (0, 512).

        Notes
        -----
        Les embeddings produits sont compatibles avec ceux générés
        par la méthode encode(), permettant de calculer des similarités
        entre des requêtes textuelles et des images.
        """

        if not queries:
            return np.empty((0, 512), dtype=np.float32)

        embeddings = self.query_model.encode(
            list(queries),
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return embeddings.astype(np.float32)
