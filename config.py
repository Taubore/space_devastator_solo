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
    taille_police_titre: int = 44
    taille_police_texte: int = 22
    taille_police_base: int = 22
    
    couleur_fond: tuple[int, int, int] = (8, 10, 20)
    couleur_texte: tuple[int, int, int] = (204, 229, 255)
    couleur_pointage: tuple[int, int, int] = (51, 153, 255)
    couleur_pointage_record: tuple[int, int, int] = (255, 51, 51)    
    couleur_bonus: tuple[int, int, int] = (255, 210, 80)
    couleur_axe_defaite : tuple[int, int, int] = (236, 42, 42)
    image_fond_ecran: str = "assets/images/fond_ecran.png"
    image_joueur: str = "assets/images/vaisseau3.png"
    image_adversaires: tuple[str, str, str, str] = (
        "assets/images/soucoupe_volante_verte.png",
        "assets/images/soucoupe_volante_bleue.png",
        "assets/images/soucoupe_volante_rouge.png",
        "assets/images/soucoupe_volante_rouge.png",
    )
         

    freq_clignotement_defaut_ms: int = 500
    freq_clignotement_joueur_touche_ms: int = 120
    duree_clignotement_joueur_touche_ms: int = 1300
    nb_vies_initiales: int = 3
    points_par_adversaire: int = 100
    points_bonus_vie_par_niveau: int = 500
    duree_animation_bonus_ms: int = 1800
    tranche_son_bonus: int = 100
    frequence_son_bonus_depart: int = 440
    increment_frequence_son_bonus: int = 18
    duree_son_bonus_ms: int = 35

    # Sons
    son_projectile_joueur: str = "assets/sons/projectile_joueur.wav"
    son_projectile_adversaire: str = "assets/sons/projectile_adversaire.wav"
    son_explosion_joueur: str = "assets/sons/explosion_joueur.wav"
    son_explosion_adversaire: str = "assets/sons/explosion_adversaire.wav"
    son_adversaire_bonus: str = "assets/sons/adversaire_bonus.wav"

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
    descente_formation_adversaires: int = 16
    increment_vitesse_formation_adversaires: int = 1
    depart_adversaire_grille_x: int = 208
    depart_adversaire_grille_y: int = limite_y_min_zone_jouable
    duree_approche_adversaire_ms: int = 50
    echelle_initiale_approche_adversaires: float = 0.50
    amplitude_flottement_adversaire: int = 3
    vitesse_flottement_adversaire: float = 0.004

     # Effets visuels
    duree_explosion_adversaire_ms: int = 220
    rayon_explosion_min: int = 5
    rayon_explosion_max: int = 40
    couleur_explosion_interne: tuple[int, int, int] = (255, 127, 0)   
    couleur_explosion_externe: tuple[int, int, int] = (255, 80, 80)

    duree_flash_tir_ms: int = 40
    rayon_flash_tir_min: int = 4
    rayon_flash_tir_max: int = 16
    couleur_flash_tir_externe: tuple[int, int, int] = (255, 180, 60)
    couleur_flash_tir_interne: tuple[int, int, int] = (255, 245, 180)    

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
