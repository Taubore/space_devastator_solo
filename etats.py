"""États principaux du jeu."""

from enum import Enum, auto


class EtatJeu(Enum):
    """Représente l'état actuel du jeu."""

    PREPARATION = auto()
    EXECUTION = auto()
    FERMETURE = auto()
    VICTOIRE = auto()
    DEFAITE = auto()
