"""Objets principaux qui composent le jeu."""

import pygame
from config import Configuration
from etats import DirectionHorizontale


class Clignotement:
    """Gère un affichage visible / caché selon une demi-période en ms."""

    def __init__(
        self,
        duree_ms: int = 500,
        visible_au_depart: bool = True,
    ) -> None:
        self.duree_ms = duree_ms
        self.visible_au_depart = visible_au_depart
        self.instant_depart = pygame.time.get_ticks()

    def est_visible(self, instant_ms: int) -> bool:
        """Indique si l'élément doit être affiché à cet instant."""

        if self.duree_ms <= 0:
            return True

        phase_visible = ((instant_ms - self.instant_depart) // self.duree_ms) % 2 == 0
        return phase_visible if self.visible_au_depart else not phase_visible

    def reinitialiser(self) -> None:
        """Relance le clignotement depuis une phase visible ou cachée initiale."""

        self.instant_depart = pygame.time.get_ticks()


class Joueur:
    """Vaisseau contrôlé par le joueur."""

    def __init__(self, config: Configuration) -> None:
        x = (config.limite_x_max_zone_jouable - config.largeur_joueur) // 2
        y = (config.limite_y_max_zone_jouable - config.hauteur_joueur)

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

        if self.rect.left < config.limite_x_min_zone_jouable:
            self.rect.left = config.limite_x_min_zone_jouable 
        
        if self.rect.right > config.limite_x_max_zone_jouable:
            self.rect.right = config.limite_x_max_zone_jouable

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

    def __init__(self) -> None:
        self.adversaires = []
        self.direction = DirectionHorizontale.DROITE

    @property
    def nombre_adversaires(self) -> int:
        """Retourne le nombre d'adversaires encore présents."""
        
        return len(self.adversaires)

    def creer_adversaires(self, config: Configuration) -> None:
        """
        Initialise tous les adversaires à partir des infos de la configuration.
        """

        self.adversaires = []

        pas_x = (
            config.largeur_adversaire
            + config.espacement_adversaire_x
        )
        pas_y = (
            config.hauteur_adversaire
            + config.espacement_adversaire_y
        )

        for lig in range(config.lignes_adversaires):
            for col in range(config.colonnes_adversaires):
                x = config.depart_adversaire_grille_x + col * pas_x
                y = config.depart_adversaire_grille_y + lig * pas_y
                self.adversaires.append(Adversaire(x, y, config))

    def traiter_collision_projectile(self, projectile_rect: pygame.Rect) -> bool:
        """
        Vérifie si projectile touche un adversaire.
        Retire l'adversaire touché et retourne True, sinon False.
        """
        for adv in self.adversaires:
            if projectile_rect.colliderect(adv.rect):
                self.adversaires.remove(adv)
                return True

        return False

    def verifier_collision(self, rect: pygame.Rect) -> Adversaire | None:
        """
        Vérfie si un des adversaires est entré en collision avec le rectangle passé en
        paramètre. Si oui, retourne l'adversaire touché, sinon retourne None.
        """
        
        for adv in self.adversaires:
            if rect.colliderect(adv.rect):
                return adv

        return None

    def mettre_a_jour(self, config: Configuration) -> None:
        """Déplace la formation et la fait descendre lorsqu'elle touche un bord."""
        
        if not self.adversaires:
            return

        decalage_x = int(self.direction) * config.vitesse_formation_adversaires

        bord_gauche = min(adv.rect.left for adv in self.adversaires)
        bord_droit = max(adv.rect.right for adv in self.adversaires)

        touche_bord_gauche = (
            bord_gauche + decalage_x <= config.limite_x_min_zone_jouable
        )
        touche_bord_droit = (
            bord_droit + decalage_x >= config.limite_x_max_zone_jouable
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
        self.limite_projectile_haut = config.limite_y_min_zone_jouable
        
    @property
    def est_sorti(self) -> bool:
        """Indique si le projectile est sorti par le haut de l'écran."""
        return self.rect.bottom < self.limite_projectile_haut

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
