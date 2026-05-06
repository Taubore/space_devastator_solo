from dataclasses import dataclass


@dataclass(frozen=True)
class ParametresNiveau:
    """
    Regroupe les paramètres d'un niveau.
    """

    numero: int
    nb_canaux_tir: int
    vitesse_formation_adversaires: int
    colonnes_adversaires: int
    lignes_adversaires: int
    espacement_adversaire_x: int
    espacement_adversaire_y: int
    adversaire_bonus_actif: bool = False
    vitesse_adversaire_bonus: int = 0
    pointage_adversaire_bonus: int = 0
    delai_min_adversaire_bonus_ms: int = 0
    delai_max_adversaire_bonus_ms: int = 0

NIVEAUX = [
    ParametresNiveau(
        numero=1,
        nb_canaux_tir=1,
        vitesse_formation_adversaires=3,
        colonnes_adversaires=6,
        lignes_adversaires=2,
        espacement_adversaire_x=80,
        espacement_adversaire_y=6,
        adversaire_bonus_actif=False,
        vitesse_adversaire_bonus=1,
        pointage_adversaire_bonus=1000,
        delai_min_adversaire_bonus_ms=2000,
        delai_max_adversaire_bonus_ms=8000,
    ),
    ParametresNiveau(
        numero=2,
        nb_canaux_tir=2,
        vitesse_formation_adversaires=3,
        colonnes_adversaires=7,
        lignes_adversaires=2,
        espacement_adversaire_x=70,
        espacement_adversaire_y=6,
        adversaire_bonus_actif=True,
        vitesse_adversaire_bonus=2,
        pointage_adversaire_bonus=1000,
        delai_min_adversaire_bonus_ms=2000,
        delai_max_adversaire_bonus_ms=8000,
    ),
    ParametresNiveau(
        numero=3,
        nb_canaux_tir=2,
        vitesse_formation_adversaires=3,
        colonnes_adversaires=7,
        lignes_adversaires=3,
        espacement_adversaire_x=70,
        espacement_adversaire_y=6,
        adversaire_bonus_actif=False,
        vitesse_adversaire_bonus=2,
        pointage_adversaire_bonus=2000,
        delai_min_adversaire_bonus_ms=2000,
        delai_max_adversaire_bonus_ms=8000,
    ),
    ParametresNiveau(
        numero=4,
        nb_canaux_tir=3,
        vitesse_formation_adversaires=4,
        colonnes_adversaires=8,
        lignes_adversaires=3,
        espacement_adversaire_x=60,
        espacement_adversaire_y=6,
        adversaire_bonus_actif=True,
        vitesse_adversaire_bonus=2,
        pointage_adversaire_bonus=2000,
        delai_min_adversaire_bonus_ms=2000,
        delai_max_adversaire_bonus_ms=8000,
    ),
    ParametresNiveau(
        numero=5,
        nb_canaux_tir=3,
        vitesse_formation_adversaires=5,
        colonnes_adversaires=8,
        lignes_adversaires=4,
        espacement_adversaire_x=60,
        espacement_adversaire_y=6,
        adversaire_bonus_actif=False,
        vitesse_adversaire_bonus=3,
        pointage_adversaire_bonus=3000,
        delai_min_adversaire_bonus_ms=2000,
        delai_max_adversaire_bonus_ms=8000,
    ),
    ParametresNiveau(
        numero=6,
        nb_canaux_tir=4,
        vitesse_formation_adversaires=5,
        colonnes_adversaires=8,
        lignes_adversaires=4,
        espacement_adversaire_x=60,
        espacement_adversaire_y=6,
        adversaire_bonus_actif=True,
        vitesse_adversaire_bonus=3,
        pointage_adversaire_bonus=3000,
        delai_min_adversaire_bonus_ms=2000,
        delai_max_adversaire_bonus_ms=8000,
    ),
    ParametresNiveau(
        numero=7,
        nb_canaux_tir=5,
        vitesse_formation_adversaires=5,
        colonnes_adversaires=8,
        lignes_adversaires=4,
        espacement_adversaire_x=60,
        espacement_adversaire_y=6,
        adversaire_bonus_actif=False,
        vitesse_adversaire_bonus=4,
        pointage_adversaire_bonus=4000,
        delai_min_adversaire_bonus_ms=2000,
        delai_max_adversaire_bonus_ms=8000,
    ),
    ParametresNiveau(
        numero=8,
        nb_canaux_tir=5,
        vitesse_formation_adversaires=5,
        colonnes_adversaires=9,
        lignes_adversaires=4,
        espacement_adversaire_x=50,
        espacement_adversaire_y=6,
        adversaire_bonus_actif=True,
        vitesse_adversaire_bonus=5,
        pointage_adversaire_bonus=4000,
        delai_min_adversaire_bonus_ms=2000,
        delai_max_adversaire_bonus_ms=8000,
    ),
    ParametresNiveau(
        numero=9,
        nb_canaux_tir=5,
        vitesse_formation_adversaires=5,
        colonnes_adversaires=9,
        lignes_adversaires=4,
        espacement_adversaire_x=50,
        espacement_adversaire_y=6,
        adversaire_bonus_actif=False,
        vitesse_adversaire_bonus=5,
        pointage_adversaire_bonus=5000,
        delai_min_adversaire_bonus_ms=2000,
        delai_max_adversaire_bonus_ms=8000,
    ),
    ParametresNiveau(
        numero=10,
        nb_canaux_tir=5,
        vitesse_formation_adversaires=5,
        colonnes_adversaires=10,
        lignes_adversaires=4,
        espacement_adversaire_x=40,
        espacement_adversaire_y=6,
        adversaire_bonus_actif=True,
        vitesse_adversaire_bonus=5,
        pointage_adversaire_bonus=5000,
        delai_min_adversaire_bonus_ms=2000,
        delai_max_adversaire_bonus_ms=8000,
    ),
]

class GestionnaireNiveaux:
    """
    Contrôle la progression entre les niveaux.

    Cette classe ne crée pas les adversaires elle-même. Elle fournit seulement
    les paramètres du niveau courant à la classe qui sait créer la formation.
    """

    def __init__(self, niveaux: list[ParametresNiveau]) -> None:
        self._niveaux = niveaux
        self._indice_niveau = 0

    @property
    def niveau_courant(self) -> ParametresNiveau:
        """
        Retourne les paramètres du niveau actuellement actif.
        """

        return self._niveaux[self._indice_niveau]

    def passer_au_niveau_suivant(self) -> bool:
        """
        Passe au prochain niveau.

        Retourne True si un niveau suivant existe.
        Retourne False si le joueur a terminé le dernier niveau.
        """

        if self._indice_niveau + 1 >= len(self._niveaux):
            return False

        self._indice_niveau += 1
        return True

    def recommencer(self) -> None:
        """
        Replace la progression au premier niveau.
        """

        self._indice_niveau = 0
