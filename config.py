"""Configuration du jeu."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Configuration:
    """Regroupe les paramètres stables du jeu."""

    largeur_fenetre: int = 1280
    hauteur_fenetre: int = 720
    images_par_seconde: int = 60

    titre: str = "Space Devastator solo"
    taille_police_base: int = 32

    couleur_fond: tuple[int, int, int] = (8, 10, 20)
    couleur_texte: tuple[int, int, int] = (230, 230, 230)

    # À retirer lorsque sprites seront créés
    couleur_joueur: tuple[int, int, int] = (80, 220, 255)
    couleur_adversaire: tuple[int, int, int] = (120, 255, 120)

    largeur_joueur: int = 96
    hauteur_joueur: int = 96
    marge_bas_joueur: int = 40

    largeur_adversaire: int = 64
    hauteur_adversaire: int = 64

    colonnes_adversaires: int = 8
    lignes_adversaires: int = 3
    espacement_adversaire_x: int = 54
    espacement_adversaire_y: int = 40
    depart_adversaire_grille_x: int = 208
    depart_adversaire_grille_y: int = 80


    