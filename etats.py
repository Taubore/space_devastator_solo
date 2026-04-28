"""États principaux du jeu."""

from enum import Enum, IntEnum, auto


class EtatJeu(Enum):
    """Représente l'état actuel du jeu."""

    PREPARATION = auto()
    APPROCHE = auto()
    EXECUTION = auto()
    FERMETURE = auto()
    VICTOIRE = auto()
    DEFAITE = auto()
    TOUCHE = auto()


class DirectionHorizontale(IntEnum):
    """Représente une direction sur l'axe horizontal"""

    GAUCHE = -1
    IMMOBILE = 0
    DROITE = 1
