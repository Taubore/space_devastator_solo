"""Objets principaux qui composent le jeu."""

import pygame
from config import Configuration
from etats import DirectionHorizontale

class Joueur:
    """Vaisseau contrôlé par le joueur."""

    def __init__(self, config: Configuration) -> None:

        x = (config.largeur_zone_jouable - config.largeur_joueur) // 2
        y = (config.hauteur_zone_jouable - config.hauteur_joueur)

        self.rect = pygame.Rect(
            x,
            y,
            config.largeur_joueur,
            config.hauteur_joueur,
        )

    def dessiner(
        self,
        surface: pygame.Surface,
        config: Configuration,
    ) -> None:
        """Dessine le joueur avec une forme simple temporaire."""

        pygame.draw.rect(surface, config.couleur_joueur, self.rect)

    def deplacer(
            self,
            direction: DirectionHorizontale,
            config: Configuration,
    ) -> None:
        
        self.rect.x += direction * config.vitesse_joueur

        if self.rect.left < config.marge_x_zone_jouable:
            self.rect.left = config.marge_x_zone_jouable 
        
        if self.rect.right > config.largeur_zone_jouable:
            self.rect.right = config.largeur_zone_jouable

class Adversaire:
    """Adversaire individuel dans la grille."""

    def __init__(self, x: int, y: int, config: Configuration) -> None:
        self.rect = pygame.Rect(
            x,
            y,
            config.largeur_adversaire,
            config.hauteur_adversaire,
        )

    def dessiner(
        self,
        surface: pygame.Surface,
        config: Configuration,
    ) -> None:
        """Dessine un alien avec une forme simple temporaire."""

        pygame.draw.rect(surface, config.couleur_adversaire, self.rect)