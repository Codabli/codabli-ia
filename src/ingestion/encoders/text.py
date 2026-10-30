"""encoders/text.py

Module d'encodage des textes pour la recherche sémantique textuelle.
"""

from typing import Sequence

import numpy as np
from sentence_transformers import SentenceTransformer

from src.constants import EMBEDDING_MODEL_TXT
from src.ingestion.encoders.base import BaseEncoder


class TextEncoder(BaseEncoder):
    """
    Encode des textes pour la recherche sémantique textuelle.

    Cette classe utilise un modèle SentenceTransformer pour transformer
    des textes en embeddings dans un espace vectoriel.

    Les embeddings sont normalisés afin de faciliter le calcul de
    similarité entre les représentations vectorielles.

    Parameters
    ----------
    model_name : str, default=EMBEDDING_MODEL_TXT
        Nom ou chemin du modèle SentenceTransformer à utiliser.

    device : str, default="cpu"
        Périphérique utilisé pour l'exécution du modèle
        (par exemple, "cpu" ou "cuda").

    Attributes
    ----------
    model_name : str
        Nom ou chemin du modèle utilisé.

    model : SentenceTransformer
        Modèle chargé pour l'encodage des textes.
    """

    def __init__(self, model_name: str = EMBEDDING_MODEL_TXT, device: str = "cpu") -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(model_name, device=device)

    def encode(self, inputs: Sequence[str]) -> np.ndarray:
        """
        Transforme une séquence de textes en embeddings normalisés.

        Les textes sont encodés par le modèle SentenceTransformer.
        Les embeddings obtenus sont normalisés et convertis en float32.

        Parameters
        ----------
        inputs : Sequence[str]
            Séquence de textes à encoder.

        Returns
        -------
        np.ndarray
            Tableau NumPy de type float32 contenant les embeddings
            normalisés des textes.

            Sa forme est (n_textes, embedding_dimension), où
            embedding_dimension correspond à la dimension des vecteurs
            produits par le modèle.

            Si la séquence est vide, retourne un tableau vide de forme
            (0, embedding_dimension).

        Notes
        -----
        Les embeddings sont normalisés, ce qui permet notamment
        de faciliter les comparaisons par similarité cosinus.
        """
        if not inputs:
            return np.empty((0, self.model.get_embedding_dimension()))

        embeddings = self.model.encode(
            list(inputs),
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return embeddings.astype(np.float32)
