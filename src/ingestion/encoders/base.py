"""encoders/base.py

Module définissant l'interface abstraite commune aux encodeurs.
"""

from abc import ABC, abstractmethod
from typing import Any, Sequence

import numpy as np


class BaseEncoder(ABC):
    """
    Interface de base commune à tous les encodeurs.

    Cette classe définit le contrat que doivent respecter les encodeurs
    chargés de transformer des données d'entrée en représentations vectorielles.
    """

    @abstractmethod
    def encode(self, inputs: Sequence[Any]) -> np.ndarray:
        """
        Transforme une séquence d'entrées en représentations vectorielles.

        Parameters
        ----------
        inputs : Sequence[Any]
            Séquence des données à encoder.

        Returns
        -------
        np.ndarray
            Tableau NumPy contenant les représentations vectorielles
            des entrées.

        Raises
        ------
        NotImplementedError
            Si la méthode n'est pas implémentée dans une classe fille.
        """
        raise NotImplementedError
