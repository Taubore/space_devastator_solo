"""Objets principaux qui composent le jeu."""

import pygame
from config import Configuration
from etats import DirectionHorizontale


class Joueur:
    """Vaisseau contrôlé par le joueur."""

    def __init__(self, config: Configuration) -> None:
        """
        Constructeur
        """
        
        self.config = config
        largeur_zone_jouable = (
            config.limite_x_max_zone_jouable
            - config.limite_x_min_zone_jouable
        )
        x = (
            config.limite_x_min_zone_jouable
            + (largeur_zone_jouable - config.largeur_joueur) // 2
        )
        y = (config.limite_y_max_zone_jouable - config.hauteur_joueur)
        self.rect = pygame.Rect(
            x,
            y,
            config.largeur_joueur,
            config.hauteur_joueur,
        )

    def dessiner(self, surface: pygame.Surface) -> None:
        """
        Dessine le joueur avec une forme simple temporaire.
        """

        pygame.draw.rect(surface, self.config.couleur_joueur, self.rect)

    def deplacer(self, direction: DirectionHorizontale) -> None:
        """
        Deplace le joueur.
        """
        
        self.rect.x += direction * self.config.vitesse_joueur

        if self.rect.left < self.config.limite_x_min_zone_jouable:
            self.rect.left = self.config.limite_x_min_zone_jouable 
        
        if self.rect.right > self.config.limite_x_max_zone_jouable:
            self.rect.right = self.config.limite_x_max_zone_jouable


class Adversaire:
    """Adversaire individuel dans la grille."""

    def __init__(self, x: int, y: int, config: Configuration) -> None:
        """
        Constructeur
        """
        self.config = config
        self.rect = pygame.Rect(
            x,
            y,
            config.largeur_adversaire,
            config.hauteur_adversaire,
        )

    def dessiner(self, surface: pygame.Surface) -> None:
        """Dessine un alien avec une forme simple temporaire."""

        pygame.draw.rect(surface, self.config.couleur_adversaire, self.rect)


class FormationAdversaires:
    """Gère le déplacement collectif des adversaires."""

    def __init__(self, config: Configuration) -> None:
        """
        Constructeur
        """
        
        self.config = config
        self.adversaires = []
        self.direction = DirectionHorizontale.DROITE

    @property
    def nombre_adversaires(self) -> int:
        """
        Retourne le nombre d'adversaires encore présents.
        """
        
        return len(self.adversaires)

    def creer_adversaires(self, vitesse: int) -> None:
        """
        Initialise tous les adversaires à partir des infos de la configuration.
        """

        self.vitesse_formation = vitesse
        self.adversaires = []

        pas_x = (
            self.config.largeur_adversaire
            + self.config.espacement_adversaire_x
        )
        pas_y = (
            self.config.hauteur_adversaire
            + self.config.espacement_adversaire_y
        )

        for lig in range(self.config.lignes_adversaires):
            for col in range(self.config.colonnes_adversaires):
                x = self.config.depart_adversaire_grille_x + col * pas_x
                y = self.config.depart_adversaire_grille_y + lig * pas_y
                self.adversaires.append(Adversaire(x, y, self.config))

    def verifier_collision(self, rect: pygame.Rect) -> Adversaire | None:
        """
        Vérfie si un des adversaires est entré en collision avec le rectangle passé en
        paramètre. Si oui, retourne l'adversaire touché, sinon retourne None.
        """
        
        for adv in self.adversaires:
            if rect.colliderect(adv.rect):
                return adv

        return None

    def mettre_a_jour(self) -> None:
        """
        Déplace la formation et la fait descendre lorsqu'elle touche un bord.
        """
        
        if not self.adversaires:
            return

        decalage_x = int(self.direction) * self.vitesse_formation

        bord_gauche = min(adv.rect.left for adv in self.adversaires)
        bord_droit = max(adv.rect.right for adv in self.adversaires)

        touche_bord_gauche = (
            bord_gauche + decalage_x <= self.config.limite_x_min_zone_jouable
        )
        touche_bord_droit = (
            bord_droit + decalage_x >= self.config.limite_x_max_zone_jouable
        )

        if touche_bord_gauche or touche_bord_droit:
            self.direction = DirectionHorizontale(-int(self.direction))

            for adv in self.adversaires:
                adv.rect.y += self.config.descente_formation_adversaires

            return

        for adv in self.adversaires:
            adv.rect.x += decalage_x

    def dessiner(self, surface: pygame.Surface) -> None:
        """
        Dessine tous les adversaires de la formation.
        """

        for adv in self.adversaires:
            adv.dessiner(surface)


class ProjectileJoueur:
    """Projectile tiré par le joueur vers le haut."""

    def __init__(self, x_centre: int, y_haut: int, config: Configuration) -> None:
        """
        Constructeur
        """

        self.config = config
        self.rect = pygame.Rect(
            0,
            0,
            config.largeur_projectile_joueur,
            config.hauteur_projectile_joueur,
        )
        self.rect.centerx = x_centre
        self.rect.bottom = y_haut
        self.limite_projectile_haut = config.limite_y_min_zone_jouable
        
    @property
    def est_sorti(self) -> bool:
        """
        Indique si le projectile est sorti par le haut de l'écran.
        """
        
        return self.rect.bottom < self.limite_projectile_haut

    def mettre_a_jour(self) -> None:
        """
        Déplace le projectile vers le haut.
        """
        
        self.rect.y -= self.config.vitesse_projectile_joueur

    def dessiner(self, surface: pygame.Surface) -> None:
        """
        Dessine temporairement le projectile sous forme de rectangle.
        """
        
        pygame.draw.rect(
            surface,
            self.config.couleur_projectile_joueur,
            self.rect,
            border_radius=4,
        )
