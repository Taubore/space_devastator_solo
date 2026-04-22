"""Programme principal du jeu Space Devastator Solo"""

import os
import sys

import pygame

from config import Configuration
from etats import EtatJeu, DirectionHorizontale
from objets import Joueur, Adversaire, FormationAdversaires, ProjectileJoueur


class Jeu:
    """Classe principale du jeu."""

    def __init__(self) -> None:
        """Initialisation de l'objet de la classe."""

        pygame.init()

        self.config = Configuration()

        # Récupération du paramètre dans launch.json pour afficher en mode fenêtré
        # ou non. Utile pour le déboguage.
        mode_fenetre = os.environ.get("MODE_FENETRE") == "1"

        self.surface_jeu = pygame.Surface(
            (self.config.largeur_fenetre, self.config.hauteur_fenetre)
        )
        self.surface_affichage, self.zone_affichage = (
            self._creer_surface_affichage(mode_fenetre)
        )

        pygame.display.set_caption(self.config.titre)

        self.horloge = pygame.time.Clock()
        self.etat = EtatJeu.PREPARATION

        self.joueur = Joueur(self.config)
        self.formation_adversaires = FormationAdversaires(
           self._creer_grille_adversaires()
        )

        self.projectile_joueur: ProjectileJoueur | None = None

        self.police_base = pygame.font.Font(None, self.config.taille_police_base)
        
        self.touche_tir_precedente = False
        self.etat = EtatJeu.EXECUTION

    def _creer_surface_affichage(
        self,
        mode_fenetre: bool,
    ) -> tuple[pygame.Surface, pygame.Rect]:
        """Crée la surface réelle d'affichage et la zone de rendu du jeu."""

        taille_jeu = (
            self.config.largeur_fenetre,
            self.config.hauteur_fenetre,
        )

        if mode_fenetre:
            surface_affichage = pygame.display.set_mode(taille_jeu)
            zone_affichage = surface_affichage.get_rect()
            return surface_affichage, zone_affichage

        surface_affichage = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        zone_affichage = pygame.Rect((0, 0), taille_jeu)
        zone_affichage.center = surface_affichage.get_rect().center
        return surface_affichage, zone_affichage

    def _creer_grille_adversaires(self) -> list[Adversaire]:
        """Crée une grille avec tous les adversaires."""

        adversaires = []

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
                adversaires.append(Adversaire(x, y, self.config))

        return adversaires

    def _traiter_evenements(self) -> None:
        """Traite les événements système et clavier."""

        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                self.etat = EtatJeu.FERMETURE

            if evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:
                    self.etat = EtatJeu.FERMETURE

                if evenement.key == pygame.K_SPACE:
                    self.etat = EtatJeu.EXECUTION

    def _mettre_a_jour(self) -> None:
        """Met à jour la logique du jeu."""
        
        if self.etat is not EtatJeu.EXECUTION:
            return

        touches = pygame.key.get_pressed()
        direction = DirectionHorizontale.IMMOBILE

        if touches[pygame.K_LEFT]:
            direction = DirectionHorizontale.GAUCHE

        if touches[pygame.K_RIGHT]:
            direction = DirectionHorizontale.DROITE

        # Gestion du bouton de tir pour éviter multiples traitement
        touche_tir = touches[pygame.K_a]
        if touche_tir and not self.touche_tir_precedente:
            self._tirer_projectile_joueur()
        self.touche_tir_precedente = touche_tir

        self.joueur.deplacer(direction, self.config)
        self.formation_adversaires.mettre_a_jour(self.config)

        if self.projectile_joueur is not None:
            self.projectile_joueur.mettre_a_jour(self.config)
            if self.projectile_joueur.est_sorti:
                self.projectile_joueur = None

    def _dessiner(self) -> None:
        """Dessine la scène complète."""

        self.surface_jeu.fill(self.config.couleur_fond)

        self.formation_adversaires.dessiner(self.surface_jeu, self.config) 

        self.joueur.dessiner(self.surface_jeu, self.config)

        if self.projectile_joueur is not None:
            self.projectile_joueur.dessiner(self.surface_jeu, self.config)

        self._dessiner_etat()
        self._presenter_image()

        pygame.display.flip()

    def _dessiner_etat(self) -> None:
        """Affiche un court texte de diagnostic de l'état courant."""

        texte = f"État : {self.etat.name} | " \
                f"Aliens : {self.formation_adversaires.nombre_adversaires}"
        image_texte = self.police_base.render(
            texte,
            True,
            self.config.couleur_texte,
        )
        self.surface_jeu.blit(image_texte, (20, 20))

    def _presenter_image(self) -> None:
        """Affiche l'image du jeu sans étirement, avec bords noirs si besoin."""

        self.surface_affichage.fill((0, 0, 0))

        if self.zone_affichage.size == self.surface_jeu.get_size():
            self.surface_affichage.blit(self.surface_jeu, self.zone_affichage)
            return

        image_redimensionnee = pygame.transform.scale(
            self.surface_jeu,
            self.zone_affichage.size,
        )
        self.surface_affichage.blit(image_redimensionnee, self.zone_affichage)

    def _tirer_projectile_joueur(self) -> None:
        """Crée un projectile joueur s'il n'y en a pas déjà un actif."""

        if self.projectile_joueur is not None:
            return

        self.projectile_joueur = ProjectileJoueur(
            self.joueur.rect.centerx,
            self.joueur.rect.top,
            self.config,
        )

    def executer(self) -> None:
        """Lance la boucle principale du jeu."""

        while self.etat is not EtatJeu.FERMETURE:
            self._traiter_evenements()
            self._mettre_a_jour()
            self._dessiner()

            self.horloge.tick(self.config.images_par_seconde)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    jeu = Jeu()
    jeu.executer()
