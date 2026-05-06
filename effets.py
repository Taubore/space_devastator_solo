"""
Regroupe les effets visuels temporaires du jeu.
"""
import pygame

from config import Configuration
from abc import ABC, abstractmethod
from commun import AfficheurTexte

class EffetVisuel(ABC):
    """
    Classe abstraite pour tous les effets visuels
    """

    def __init__(self, config: Configuration) -> None:
        """
        Initialise les informations communes à tous les effets visuels.
        """
        
        self.config = config
        self.instant_depart = pygame.time.get_ticks()
        self.est_terminee = False

    @abstractmethod
    def mettre_a_jour(self) -> None:
        pass

    @abstractmethod
    def dessiner(self, surface: pygame.Surface) -> None:
        pass

class Explosion(EffetVisuel):
    """
    Petite explosion visuelle temporaire.

    L'explosion est volontairement simple : quelques cercles qui grossissent
    rapidement, puis l'objet se marque comme terminé.
    """

    def __init__(self, centre: tuple[int, int], pointage: int, config: Configuration) -> None:
        """
        Initialise l'explosion à une position donnée.
        """

        super().__init__(config)
        self.centre = centre
        self.pointage = pointage

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

        # On affiche le pointage selon le type d'adversaire
        police = pygame.font.Font(None, self.config.taille_police_pointage_explosion)
        surface_txt = police.render(str(self.pointage), True, self.config.couleur_pointage)
        pos = self.centre[0]-30, self.centre[1]-50
        surface.blit(surface_txt, pos)

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

class FlashTir(EffetVisuel):
    """
    Petit flash visuel affiché au départ du projectile du joueur.

    L'effet est très court : il sert seulement à renforcer la sensation
    immédiate du tir, sans devenir une animation complexe.
    """

    def __init__(self, centre: tuple[int, int], config: Configuration) -> None:
        """
        Initialise le flash à la position du canon.
        """

        super().__init__(config)
        self.centre = centre

    def mettre_a_jour(self) -> None:
        """
        Met à jour l'état du flash.
        """

        temps_ecoule = pygame.time.get_ticks() - self.instant_depart

        if temps_ecoule >= self.config.duree_flash_tir_ms:
            self.est_terminee = True

    def dessiner(self, surface: pygame.Surface) -> None:
        """
        Dessine un flash court qui grossit légèrement avant de disparaître.
        """

        temps_ecoule = pygame.time.get_ticks() - self.instant_depart
        progression = temps_ecoule / self.config.duree_flash_tir_ms
        progression = min(progression, 1.0)

        rayon = int(
            self.config.rayon_flash_tir_min
            + (
                self.config.rayon_flash_tir_max
                - self.config.rayon_flash_tir_min
            )
            * progression
        )

        pygame.draw.circle(
            surface,
            self.config.couleur_flash_tir_externe,
            self.centre,
            rayon,
            width=2,
        )

        pygame.draw.circle(
            surface,
            self.config.couleur_flash_tir_interne,
            self.centre,
            max(2, rayon // 3),
        )