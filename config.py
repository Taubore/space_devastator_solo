""" 
Configuration du jeu.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Configuration:
    """Regroupe les paramètres stables du jeu."""

    largeur_fenetre: int = 1280
    hauteur_fenetre: int = 800
    images_par_seconde: int = 60

    limite_x_min_zone_jouable: int = 30
    limite_y_min_zone_jouable: int = 60
    limite_x_max_zone_jouable: int = largeur_fenetre - limite_x_min_zone_jouable
    limite_y_max_zone_jouable: int = hauteur_fenetre - limite_y_min_zone_jouable

    titre: str = "Space Devastator solo"
    taille_police_titre: int = 50
    taille_police_texte: int = 22
    taille_police_base: int = 18
    
    couleur_fond: tuple[int, int, int] = (8, 10, 20)
    couleur_texte: tuple[int, int, int] = (230, 230, 230)
    couleur_axe_defaite : tuple[int, int, int] = (120, 0, 0)
    image_fond_ecran: str = "assets/images/fond_ecran.png"
    image_joueur: str = "assets/images/vaisseau.png"
    image_adversaire: str = "assets/images/soucoupe_volante.png"

    duree_clignotement_defaut_ms: int = 500
    nb_vies_initiales: int = 3
    points_par_adversaire: int = 100

    # Joueur
    couleur_joueur: tuple[int, int, int] = (80, 220, 255)  # À retirer lorsque sprite

    largeur_joueur: int = 96
    hauteur_joueur: int = 96
    vitesse_joueur: int = 7

    axe_y_defaite: int = limite_y_max_zone_jouable - hauteur_joueur - 25
    axe_y_avertissement : int = axe_y_defaite - 100

    # Adversaires
    couleur_adversaire: tuple[int, int, int] = (120, 255, 120) # À retirer 
    
    largeur_adversaire: int = 64
    hauteur_adversaire: int = 64
    vitesse_initiale_formation_adversaires: int = 2
    descente_formation_adversaires: int = 16
    increment_vitesse_formation_adversaires: int = 1
    colonnes_adversaires: int = 8
    lignes_adversaires: int = 3
    espacement_adversaire_x: int = 54
    espacement_adversaire_y: int = 40
    depart_adversaire_grille_x: int = 208
    depart_adversaire_grille_y: int = limite_y_min_zone_jouable
    duree_approche_adversaire_ms: int = 50
    echelle_initiale_approche_adversaires: float = 0.50

     # Effets visuels
    duree_explosion_adversaire_ms: int = 220
    rayon_explosion_min: int = 5
    rayon_explosion_max: int = 40
    couleur_explosion_interne: tuple[int, int, int] = (255, 127, 0)   
    couleur_explosion_externe: tuple[int, int, int] = (255, 80, 80)


#    couleur_explosion_externe: tuple[int, int, int] = (255, 120, 0)
#    couleur_explosion_interne: tuple[int, int, int] = (255, 230, 80)   

    # Projectile joueur
    couleur_projectile_joueur: tuple[int, int, int] = (255, 127, 0)  # À retirer

    largeur_projectile_joueur: int = 6
    hauteur_projectile_joueur: int = 32
    vitesse_projectile_joueur: int = 14

    # Projectile adversaires
    couleur_projectile_adversaire: tuple[int, int, int] = (255, 0, 0)  # À retirer

    largeur_projectile_adversaire: int = 3
    hauteur_projectile_adversaire: int = 18
    vitesse_projectile_adversaire: int = 6

    delai_tir_adversaires_initial: int = 2500
    increment_delai_tir_adversaires: int = -500
