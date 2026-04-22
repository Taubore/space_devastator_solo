"""Configuration du jeu."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Configuration:
    """Regroupe les paramètres stables du jeu."""

    largeur_fenetre: int = 1280
    hauteur_fenetre: int = 800
    images_par_seconde: int = 60

    marge_x_zone_jouable: int = 50
    marge_y_zone_jouable: int = 50
    largeur_zone_jouable: int = largeur_fenetre - marge_x_zone_jouable
    hauteur_zone_jouable: int = hauteur_fenetre - marge_y_zone_jouable

    titre: str = "Space Devastator solo"
    taille_police_base: int = 16

    couleur_fond: tuple[int, int, int] = (8, 10, 20)
    couleur_texte: tuple[int, int, int] = (230, 230, 230)

    # Joueur
    couleur_joueur: tuple[int, int, int] = (80, 220, 255)  # À retirer lorsque sprite

    largeur_joueur: int = 96
    hauteur_joueur: int = 96
    vitesse_joueur: int = 7

    # Adversaires
    couleur_adversaire: tuple[int, int, int] = (120, 255, 120) # À retirer 
    
    largeur_adversaire: int = 64
    hauteur_adversaire: int = 64
    vitesse_formation_adversaires: int = 1
    descente_formation_adversaires: int = 16
    colonnes_adversaires: int = 8
    lignes_adversaires: int = 3
    espacement_adversaire_x: int = 54
    espacement_adversaire_y: int = 40
    depart_adversaire_grille_x: int = 208
    depart_adversaire_grille_y: int = marge_y_zone_jouable

    # Projectile
    couleur_projectile_joueur: tuple[int, int, int] = (120, 220, 255)  # À retirer

    largeur_projectile_joueur: int = 12
    hauteur_projectile_joueur: int = 32
    vitesse_projectile_joueur: int = 10
