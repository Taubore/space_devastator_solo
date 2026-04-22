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

class FormationAdversaires:
    """Gère le déplacement collectif des adversaires."""

    def __init__(self, adversaires: list[Adversaire]) -> None:
        self.adversaires = adversaires
        self.direction = DirectionHorizontale.DROITE

    @property
    def nombre_adversaires(self) -> int:
        """Retourne le nombre d'adversaires encore présents."""
        return len(self.adversaires)

    def mettre_a_jour(self, config: Configuration) -> None:
        """Déplace la formation et la fait descendre lorsqu'elle touche un bord."""
        if not self.adversaires:
            return

        decalage_x = int(self.direction) * config.vitesse_formation_adversaires

        bord_gauche = min(adv.rect.left for adv in self.adversaires)
        bord_droit = max(adv.rect.right for adv in self.adversaires)

        touche_bord_gauche = (
            bord_gauche + decalage_x <= config.marge_x_zone_jouable
        )
        touche_bord_droit = (
            bord_droit + decalage_x >= config.largeur_zone_jouable
        )

        if touche_bord_gauche or touche_bord_droit:
            self.direction = DirectionHorizontale(-int(self.direction))

            for adv in self.adversaires:
                adv.rect.y += config.descente_formation_adversaires

            return

        for adv in self.adversaires:
            adv.rect.x += decalage_x

    def dessiner(
        self,
        surface: pygame.Surface,
        config: Configuration,
    ) -> None:
        """Dessine tous les adversaires de la formation."""

        for adv in self.adversaires:
            adv.dessiner(surface, config)

class ProjectileJoueur:
    """Projectile tiré par le joueur vers le haut."""

    def __init__(self, x_centre: int, y_haut: int, config: Configuration) -> None:
        self.rect = pygame.Rect(
            0,
            0,
            config.largeur_projectile_joueur,
            config.hauteur_projectile_joueur,
        )
        self.rect.centerx = x_centre
        self.rect.bottom = y_haut

    @property
    def est_sorti(self) -> bool:
        """Indique si le projectile est sorti par le haut de l'écran."""
        return self.rect.bottom < 0

    def mettre_a_jour(self, config: Configuration) -> None:
        """Déplace le projectile vers le haut."""
        self.rect.y -= config.vitesse_projectile_joueur

    def dessiner(
        self,
        surface: pygame.Surface,
        config: Configuration,
    ) -> None:
        """Dessine temporairement le projectile sous forme de rectangle."""
        pygame.draw.rect(
            surface,
            config.couleur_projectile_joueur,
            self.rect,
            border_radius=4,
        )