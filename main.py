"""
Programme principal du jeu Space Devastator Solo
"""

import os
import sys
import random

import pygame


from config import Configuration
from etats import EtatJeu, DirectionHorizontale
from commun import Minuteur, Clignotement
from objets import (
    Joueur,
    Adversaire,
    FormationAdversaires,
    ProjectileJoueur,
    ProjectileAdversaire,
)


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

        self.image_fond = self._charger_image_fond()

        pygame.display.set_caption(self.config.titre)

        self.horloge = pygame.time.Clock()
        self.etat = EtatJeu.PREPARATION
        self.tir_adversaires = Minuteur(self.config.delai_tir_adversaires_initial, False)

        self.joueur = Joueur(self.config)
        self.formation_adversaires = FormationAdversaires(self.config)

        self.projectile_joueur: ProjectileJoueur | None = None
        self.projectile_adversaire: ProjectileAdversaire| None = None
        self.clignotement_defaut = Clignotement(
            self.config.duree_clignotement_defaut_ms
        )
        
        self.police_titre = pygame.font.Font(None, self.config.taille_police_titre)
        self.police_texte = pygame.font.Font(None, self.config.taille_police_texte)
        self.police_base = pygame.font.Font(None, self.config.taille_police_base)

    def _charger_image_fond(self) -> pygame.Surface:
        """
        Charge l'image de fond et l'adapte à la surface logique du jeu.
        """

        image_fond = pygame.image.load(self.config.image_fond_ecran).convert()
        return pygame.transform.smoothscale(
            image_fond,
            (self.config.largeur_fenetre, self.config.hauteur_fenetre),
        )

    def _initialiser_partie(self) -> None:
        """
        Initialise une nouvelle partie
        """

        self.nombre_vies = self.config.nb_vies_initiales
        self.pointage = 0
        self.vitesse_formation_adversaires = self.config.vitesse_initiale_formation_adversaires
        self.projectiles_adversaires: list[ProjectileAdversaire] = []
        self.tir_adversaires.changer_duree(self.config.delai_tir_adversaires_initial)

        # Faux rectangle (en fait c'est une ligne) qui délimite la zone où si un 
        # adversaire s'invite, le joueur perd la partie
        self.rect_defaite = pygame.Rect (
            self.config.limite_x_min_zone_jouable,
            self.config.axe_y_defaite,
            self.config.limite_x_max_zone_jouable - \
                self.config.limite_x_min_zone_jouable,
            1,
        )

        self.rect_defaite_proche = pygame.Rect(
            self.config.limite_x_min_zone_jouable,
            self.config.axe_y_avertissement,
            self.config.limite_x_max_zone_jouable - \
                self.config.limite_x_min_zone_jouable,
            1,
        )

    def _nouveau_tableau(self) -> None:
        """
        Initialise une nouvelle session en début de partie ou après avoir éliminé
        tous les adversaires.
        """

        self.touche_tir_precedente = False
        self.defaite_imminente = False 
        self.projectile_joueur = None
        self.projectiles_adversaires = []

        duree_tir = self.config.delai_tir_adversaires_initial + \
            self.config.increment_delai_tir_adversaires
        self.tir_adversaires.changer_duree(duree_tir)

        self.clignotement_defaut.reinitialiser()
        self.formation_adversaires.creer_adversaires(self.vitesse_formation_adversaires)

    def _creer_surface_affichage(self, mode_fenetre: bool) -> tuple[pygame.Surface, pygame.Rect]:
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
                    if self.etat is EtatJeu.VICTOIRE or self.etat is EtatJeu.PREPARATION:
                        self._nouveau_tableau()
                    if self.etat is EtatJeu.DEFAITE:
                        self._initialiser_partie()
                        self._nouveau_tableau()
                    self.etat = EtatJeu.EXECUTION

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
        self.joueur.deplacer(direction)
        self.formation_adversaires.mettre_a_jour()

        # Gestion du bouton de tir
        touche_tir = touches[pygame.K_a]
        if touche_tir and not self.touche_tir_precedente:
            self._tirer_projectile_joueur()
        self.touche_tir_precedente = touche_tir

        # Gestion du projectile du joueur
        if self.projectile_joueur is not None:
            self.projectile_joueur.mettre_a_jour()
            self._gerer_collisions_adversaires()
            if self.projectile_joueur is not None and self.projectile_joueur.est_sorti:
                self.projectile_joueur = None

        # Gestion des projectiles des adversaires
        liste_adv = self.formation_adversaires.trouver_tireurs_valides()
        nb_adv = len(liste_adv)
        if nb_adv != 0:
            tireur = random.randint(0, nb_adv - 1)
            if self.tir_adversaires.est_termine():
                self.projectiles_adversaires.append(ProjectileAdversaire(liste_adv[tireur], 
                                                                         self.config))
                self.tir_adversaires.reinitialiser()

        # Met à jour les projectiles des adversaires et retire le projectile s'il est sorti
        # de l'écran
        for pa in self.projectiles_adversaires:
            pa.mettre_a_jour()
            if pa.est_sorti:
                self.projectiles_adversaires.remove(pa)

        # Vérification si la défaite est proche
        if (self.etat is EtatJeu.EXECUTION
            and self.formation_adversaires.verifier_collision(self.rect_defaite_proche)
        ):
            self.defaite_imminente = True
            # Vérification si adversaire a atteint la ligne de défaite, si oui défaite immédiate
            if self.formation_adversaires.verifier_collision(self.rect_defaite) is not None:
                self.etat = EtatJeu.DEFAITE

        # Vérification si collisions avec le joueur
        if self._gerer_collisions_joueur() is True:
            self.nombre_vies -= 1
            self.etat = EtatJeu.DEFAITE if self.nombre_vies <= 0 else EtatJeu.TOUCHE

        # Vérfication de la victoire et de la défaite
        if self.formation_adversaires.nombre_adversaires == 0:
            self.etat = EtatJeu.VICTOIRE
            self.vitesse_formation_adversaires += \
                self.config.increment_vitesse_formation_adversaires

    def _dessiner(self) -> None:
        """
        Dessine la scène complète.
        """

        self.surface_jeu.blit(self.image_fond, (0, 0))
        temps_actuel = pygame.time.get_ticks()

        self.formation_adversaires.dessiner(self.surface_jeu) 

        if self.etat is not EtatJeu.TOUCHE and self.etat is not EtatJeu.DEFAITE :
            self.joueur.dessiner(self.surface_jeu)

        # Dessiner l'axe de défaite, il restera affiché jusqu'à une défaite ou victoire.
        if (
            self.etat is EtatJeu.EXECUTION
            and self.defaite_imminente
            and self.clignotement_defaut.est_visible(temps_actuel)
        ):
            pygame.draw.rect(
                self.surface_jeu,
                self.config.couleur_axe_defaite,
                self.rect_defaite,
            )

        if self.projectile_joueur is not None:
            self.projectile_joueur.dessiner(self.surface_jeu)

        for pa in self.projectiles_adversaires:
            pa.dessiner(self.surface_jeu)

        if self.etat is EtatJeu.PREPARATION:
            self._dessiner_demarrage()
        elif self.etat is EtatJeu.TOUCHE:
            self._dessiner_touche()
        elif self.etat is EtatJeu.VICTOIRE:
            self._dessiner_victoire()
        elif self.etat is EtatJeu.DEFAITE:
            self._dessiner_defaite()

        self._dessiner_etat()
        self._presenter_image()

        pygame.display.flip()

    def _dessiner_etat(self) -> None:
        """
        Affiche un court texte de diagnostic de l'état courant.
        """

        texte = f"Pointage : {self.pointage}    " \
                f"Envahisseurs : {self.formation_adversaires.nombre_adversaires}    " \
                f"Vies : {self.nombre_vies}"
        image_texte = self.police_base.render(
            texte,
            True,
            self.config.couleur_texte,
        )
        self.surface_jeu.blit(image_texte, (20, 20))

    def _dessiner_demarrage(self) -> None:
        """
        Affiche le titre du jeu et l'instruction pour démarrer.
        """

        texte_1 = self.police_titre.render(
            self.config.titre,
            True,
            self.config.couleur_texte,
        )
        texte_2 = self.police_texte.render(
            "Appuyez ESPACE pour démarrer",
            True,
            self.config.couleur_texte,
        )

        rect_1 = texte_1.get_rect(
            center=(
                self.surface_jeu.get_width() // 2,
                self.surface_jeu.get_height() // 3
            )
        )
        rect_2 = texte_2.get_rect(
            midtop=(rect_1.centerx, rect_1.bottom + 24)
        )

        self.surface_jeu.blit(texte_1, rect_1)
        self.surface_jeu.blit(texte_2, rect_2)

    def _dessiner_victoire(self) -> None:
        """
        Affiche la victoire et un message pour poursuivre
        """

        texte_1 = self.police_titre.render(
            "Bravo! Vous avez vaincu tous les envahisseurs!",
            True,
            self.config.couleur_texte,
        )
        texte_2 = self.police_texte.render(
            "Appuyez ESPACE pour poursuivre. D'autres s'en viennent...",
            True,
            self.config.couleur_texte,
        )

        rect_1 = texte_1.get_rect(
            center=(
                self.surface_jeu.get_width() // 2,
                self.surface_jeu.get_height() // 3
            )
        )
        rect_2 = texte_2.get_rect(
            midtop=(rect_1.centerx, rect_1.bottom + 24)
        )

        self.surface_jeu.blit(texte_1, rect_1)
        self.surface_jeu.blit(texte_2, rect_2)

    def _dessiner_touche(self) -> None:
        """
        Affiche un message lorsque le joueur a été touché et qu'il lui reste encore plus d'une vie.
        """

        if self.nombre_vies > 0:
            texte_1 = self.police_texte.render(
                "Vaisseau touché! Appuyer ESPACE pour continuer...",
                True,
                self.config.couleur_texte,
            )

            rect_1 = texte_1.get_rect(
                center=(
                    self.surface_jeu.get_width() // 2,
                    self.surface_jeu.get_height() - 100
                )
            )

            self.surface_jeu.blit(texte_1, rect_1)


    def _dessiner_defaite(self) -> None:
        """
        Affiche un message comme quoi le joueur s'est fait envahir, qu'il a perdu.
        """

        texte_1 = self.police_titre.render(
            "La terre a été envahie par les extraterrestres!",
            True,
            self.config.couleur_texte,
        )
        texte_2 = self.police_texte.render(
            "Appuyez ESPACE pour une nouvelle partie.",
            True,
            self.config.couleur_texte,
        )

        rect_1 = texte_1.get_rect(
            center=(
                self.surface_jeu.get_width() // 2,
                self.surface_jeu.get_height() // 3
            )
        )
        rect_2 = texte_2.get_rect(
            midtop=(rect_1.centerx, rect_1.bottom + 24)
        )

        self.surface_jeu.blit(texte_1, rect_1)
        self.surface_jeu.blit(texte_2, rect_2)

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
            self.joueur.rect.top + self.config.hauteur_projectile_joueur,
            self.config,
        )

    def _gerer_collisions_adversaires(self) -> None:
        """
        Gère les collisions d'un projectile du joueur avec les adversaires
        """
        
        if self.projectile_joueur is not None:
            adv = self.formation_adversaires.verifier_collision(self.projectile_joueur.rect)
            if adv is not None:
                self.formation_adversaires.adversaires.remove(adv)
                self.projectile_joueur = None

    def _gerer_collisions_joueur(self) -> bool:
        """
        Gère les collisions des projectiles adversaire avec le joueur. 
        S'assure de retirer le projectile de la liste s'il y a collision.
        Retour : true si collision.
        """
        
        if len(self.projectiles_adversaires) > 0:
            for pa in self.projectiles_adversaires:
                if self.joueur.verifier_collision(pa.rect):
                    self.projectiles_adversaires.remove(pa)
                    return True

        return False

    def executer(self) -> None:
        """
        Lance la boucle principale du jeu.
        """

        self._initialiser_partie()

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
