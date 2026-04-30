"""
Regroupe les effets visuels temporaires du jeu.
"""
import pygame

from config import Configuration

class Explosion:
    """
    Petite explosion visuelle temporaire.

    L'explosion est volontairement simple : quelques cercles qui grossissent
    rapidement, puis l'objet se marque comme terminé.
    """

    def __init__(self, centre: tuple[int, int], config: Configuration) -> None:
        """
        Initialise l'explosion à une position donnée.
        """

        self.config = config
        self.centre = centre
        self.instant_depart = pygame.time.get_ticks()
        self.est_terminee = False

    def mettre_a_jour(self) -> None:
        """
        Met à jour l'état de l'explosion.
        """

        temps_ecoule = pygame.time.get_ticks() - self.instant_depart

        if temps_ecoule >= self.config.duree_explosion_adversaire_ms:
            self.est_terminee = True

    def dessiner(self, surface: pygame.Surface) -> None:
        """
        Dessine l'explosion selon sa progression.
        """

        temps_ecoule = pygame.time.get_ticks() - self.instant_depart
        progression = temps_ecoule / self.config.duree_explosion_adversaire_ms
        progression = min(progression, 1.0)

        rayon = int(
            self.config.rayon_explosion_min
            + (
                self.config.rayon_explosion_max
                - self.config.rayon_explosion_min
            )
            * progression
        )

        # Le cercle externe grossit rapidement et donne l'impression d'un souffle.
        pygame.draw.circle(
            surface,
            self.config.couleur_explosion_externe,
            self.centre,
            rayon,
            width=3,
        )

        # Le cercle interne reste plus petit et donne un centre lumineux à l'impact.
        pygame.draw.circle(
            surface,
            self.config.couleur_explosion_interne,
            self.centre,
            max(2, rayon // 3),
        )