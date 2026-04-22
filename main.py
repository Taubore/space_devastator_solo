"""Programme principal du jeu Space Devastator Solo"""

import os
import sys

import pygame

from config import Configuration
from etats import EtatJeu, DirectionHorizontale
from objets import Joueur, Adversaire, FormationAdversaires, ProjectileJoueur


class Jeu:
    """
    Classe principale du jeu.
    """

    def __init__(self) -> None:
        """
        Initialisation de l'objet de la classe.
        """

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
        self.formation_adversaires = FormationAdversaires()

        self.projectile_joueur: ProjectileJoueur | None = None
        
        self.police_titre = pygame.font.Font(None, self.config.taille_police_titre)
        self.police_texte = pygame.font.Font(None, self.config.taille_police_texte)
        self.police_base = pygame.font.Font(None, self.config.taille_police_base)

    def _initialiser_session(self) -> None:
        """
        Initialise une nouvelle session en début de partie ou après avoir éliminé
        tous les adversaires.
        """

        self.touche_tir_precedente = False
        self.formation_adversaires.creer_adversaires(self.config)


    def _creer_surface_affichage(
        self,
        mode_fenetre: bool,
    ) -> tuple[pygame.Surface, pygame.Rect]:
        """
        Crée la surface réelle d'affichage et la zone de rendu du jeu.
        """

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

    def _traiter_evenements(self) -> None:
        """
        Traite les événements système et clavier.
        """

        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                self.etat = EtatJeu.FERMETURE

            if evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:
                    self.etat = EtatJeu.FERMETURE

                if (
                    self.etat is not EtatJeu.EXECUTION 
                    and evenement.key == pygame.K_SPACE
                ):
                    self.etat = EtatJeu.EXECUTION
                    self._initialiser_session()        

    def _mettre_a_jour(self) -> None:
        """
        Met à jour la logique du jeu.
        """
        
        if self.etat is not EtatJeu.EXECUTION:
            return

        touches = pygame.key.get_pressed()
        direction = DirectionHorizontale.IMMOBILE

        if touches[pygame.K_LEFT]:
            direction = DirectionHorizontale.GAUCHE

        if touches[pygame.K_RIGHT]:
            direction = DirectionHorizontale.DROITE

        # Gestion des déplacements
        self.joueur.deplacer(direction, self.config)
        self.formation_adversaires.mettre_a_jour(self.config)

        # Gestion du bouton de tir
        touche_tir = touches[pygame.K_a]
        if touche_tir and not self.touche_tir_precedente:
            self._tirer_projectile_joueur()
        self.touche_tir_precedente = touche_tir

        # Gestion du projectile
        if self.projectile_joueur is not None:
            self.projectile_joueur.mettre_a_jour(self.config)
            self._gerer_collision_projectile_adversaires()
            if self.projectile_joueur is not None and self.projectile_joueur.est_sorti:
                self.projectile_joueur = None

        # Vérfication de la victoire et de la défaite
        if self.etat == EtatJeu.EXECUTION:
            if self.formation_adversaires.nombre_adversaires == 0:
                self.etat = EtatJeu.VICTOIRE
                self.config.vitesse_formation_adversaires += \
                    self.config.increment_vitesse_formation_adversaires

    def _dessiner(self) -> None:
        """
        Dessine la scène complète.
        """

        self.surface_jeu.fill(self.config.couleur_fond)

        self.formation_adversaires.dessiner(self.surface_jeu, self.config) 

        self.joueur.dessiner(self.surface_jeu, self.config)
        self._dessiner_ligne_repere_joueur()

        if self.projectile_joueur is not None:
            self.projectile_joueur.dessiner(self.surface_jeu, self.config)

        if self.etat is EtatJeu.PREPARATION:
            self._dessiner_ecran_demarrage()

        if self.etat is EtatJeu.VICTOIRE:
            self._dessiner_ecran_victoire()

        self._dessiner_etat()
        self._presenter_image()

        pygame.display.flip()

    def _dessiner_etat(self) -> None:
        """
        Affiche un court texte de diagnostic de l'état courant.
        """

        texte = f"État : {self.etat.name} | " \
                f"Aliens : {self.formation_adversaires.nombre_adversaires}"
        image_texte = self.police_base.render(
            texte,
            True,
            self.config.couleur_texte,
        )
        self.surface_jeu.blit(image_texte, (20, 20))

    def _dessiner_ecran_demarrage(self) -> None:
        """
        Affiche le titre du jeu et l'instruction pour démarrer.
        """

        image_titre = self.police_titre.render(
            self.config.titre,
            True,
            self.config.couleur_texte,
        )
        image_instruction = self.police_texte.render(
            "Appuyez ESPACE pour démarrer",
            True,
            self.config.couleur_texte,
        )

        rect_titre = image_titre.get_rect(
            center=(
                self.surface_jeu.get_width() // 2,
                self.surface_jeu.get_height() // 3
            )
        )
        rect_instruction = image_instruction.get_rect(
            midtop=(rect_titre.centerx, rect_titre.bottom + 24)
        )

        self.surface_jeu.blit(image_titre, rect_titre)
        self.surface_jeu.blit(image_instruction, rect_instruction)

    def _dessiner_ecran_victoire(self) -> None:
        """
        Affiche la victoire et un message pour poursuivre
        """

        image_victoire = self.police_titre.render(
            "Bravo! Vous avez vaincu tous les envahisseurs!",
            True,
            self.config.couleur_texte,
        )
        image_instruction = self.police_texte.render(
            "Appuyez ESPACE pour poursuivre. D'autres s'en viennent...",
            True,
            self.config.couleur_texte,
        )

        rect_titre = image_victoire.get_rect(
            center=(
                self.surface_jeu.get_width() // 2,
                self.surface_jeu.get_height() // 3
            )
        )
        rect_instruction = image_instruction.get_rect(
            midtop=(rect_titre.centerx, rect_titre.bottom + 24)
        )

        self.surface_jeu.blit(image_victoire, rect_titre)
        self.surface_jeu.blit(image_instruction, rect_instruction)

    def _dessiner_ligne_repere_joueur(self) -> None:
        """
        Trace une ligne repère au-dessus du joueur.
        """

        pygame.draw.line(
            self.surface_jeu,
            (120, 0, 0),
            (self.config.limite_x_min_zone_jouable, self.config.ligne_defaite),
            (self.config.limite_x_max_zone_jouable, self.config.ligne_defaite),
            1,
        )

    def _presenter_image(self) -> None:
        """
        Affiche l'image du jeu sans étirement, avec bords noirs si besoin.
        """

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
        """
        Crée un projectile joueur s'il n'y en a pas déjà un actif.
        """

        if self.projectile_joueur is not None:
            return

        self.projectile_joueur = ProjectileJoueur(
            self.joueur.rect.centerx,
            self.joueur.rect.top,
            self.config,
        )

    def _gerer_collision_projectile_adversaires(self) -> None:
        """
        Gère la collision entre le projectile joueur et les adversaires.
        """
        
        if self.projectile_joueur is None:
            return

        adversaire_touche = self.formation_adversaires.traiter_collision_projectile(
            self.projectile_joueur.rect
        )

        if adversaire_touche:
            self.projectile_joueur = None

    def executer(self) -> None:
        """
        Lance la boucle principale du jeu.
        """

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
