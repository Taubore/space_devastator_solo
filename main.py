"""
Programme principal du jeu Space Devastator Solo
"""

import os
import sys
import random

import pygame

from config import Configuration
from etats import EtatJeu, DirectionHorizontale
from commun import Minuteur, Clignotement, AfficheurTexte
from effets import EffetVisuel, Explosion, FlashTir
from objets import (
    Joueur,
    FormationAdversaires,
    AnimationApprocheAdversaires,
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
        pygame.mixer.init()

        self.config = Configuration()

        # Récupération du paramètre dans launch.json pour afficher en mode fenêtré
        # ou non. Utile pour le déboguage.
        mode_fenetre = os.environ.get("MODE_FENETRE") == "1"

        self.surface_jeu = pygame.Surface(
            (self.config.largeur_fenetre, self.config.hauteur_fenetre)
        )
        self.surface_affichage, self.zone_affichage = (self._creer_surface_affichage(mode_fenetre))

        # On cache le curseur de la souris
        pygame.mouse.set_visible(False)

        self.image_fond = self._charger_image_fond()

        self._charger_sons()

        pygame.display.set_caption(self.config.titre)

        self.horloge = pygame.time.Clock()
        self.tir_adversaires = Minuteur(self.config.delai_tir_adversaires_initial, False)
        self.duree_clignotement_joueur_touche = Minuteur(
            self.config.duree_clignotement_joueur_touche_ms, False
            )

        self.joueur = Joueur(self.config)
        self.formation_adversaires = FormationAdversaires(self.config)
        self.animation_approche_adversaires = AnimationApprocheAdversaires(self.config)

        self.projectile_joueur: ProjectileJoueur | None = None
        self.projectiles_adversaires: list[ProjectileAdversaire] = []
        self.effets_visuels: list[EffetVisuel] = []
        
        self.clignotement_defaut = Clignotement(self.config.freq_clignotement_defaut_ms)
        self.clignotement_joueur_touche = Clignotement(
            self.config.freq_clignotement_joueur_touche_ms
        )
        
        # Objet utilitaire pour afficher du texte à l'écran.
        self.afficheur_texte = AfficheurTexte(
            self.surface_jeu,
            self.config.taille_police_texte,
            self.config.couleur_texte,
        )

        self.etat = EtatJeu.PREPARATION

    def executer(self) -> None:
        """
        Lance la boucle principale du jeu.
        """

        self._demarrer_nouvelle_partie()

        while self.etat is not EtatJeu.FERMETURE:
            self._mettre_a_jour()
            self._dessiner()
            self._traiter_evenements()

            self.horloge.tick(self.config.images_par_seconde)

        pygame.quit()
        sys.exit()

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

                if evenement.key == pygame.K_SPACE:
                    if (
                        self.etat is EtatJeu.VICTOIRE
                        or self.etat is EtatJeu.PREPARATION
                    ):
                        self._demarrer_nouveau_tableau()
                        self.etat = EtatJeu.APPROCHE
                    elif self.etat is EtatJeu.DEFAITE:
                        self._demarrer_nouvelle_partie()
                        self.etat = EtatJeu.APPROCHE
                    elif self.etat is EtatJeu.TOUCHE:
                        self._reprendre_apres_touche()
                        self.etat = EtatJeu.EXECUTION


    def _mettre_a_jour(self) -> None:
        """
        Met à jour la logique du jeu.
        """
        
        self._mettre_a_jour_effets_visuels()

        if self.etat is EtatJeu.APPROCHE:
            if self.animation_approche_adversaires.mettre_a_jour():
                self.tir_adversaires.reinitialiser()
                self.etat = EtatJeu.EXECUTION
            return

        if (
            self.etat is EtatJeu.TOUCHE 
            and self.duree_clignotement_joueur_touche.est_termine()
        ):
           self._reprendre_apres_touche()
           self.etat = EtatJeu.EXECUTION


        touches = pygame.key.get_pressed()
        direction = DirectionHorizontale.IMMOBILE

        if touches[pygame.K_LEFT]:
            direction = DirectionHorizontale.GAUCHE

        if touches[pygame.K_RIGHT]:
            direction = DirectionHorizontale.DROITE

        # Gestion des déplacements
        self.joueur.deplacer(direction)
        self.formation_adversaires.mettre_a_jour()

        # JALON important - Au delà de ce point le traitement n'est que pour le mode EXECUTION
        if self.etat is not EtatJeu.EXECUTION:
            return

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
                self.sons["projectile_adversaire"].play()
                self.projectiles_adversaires.append(ProjectileAdversaire(liste_adv[tireur], 
                                                                         self.config))
                self.tir_adversaires.reinitialiser()

        # Met à jour les projectiles des adversaires et rebâtit une liste de projectiles avec 
        # ceux qui ne sont pas sortis
        for pa in self.projectiles_adversaires:
            pa.mettre_a_jour()
        
        self.projectiles_adversaires = [
            pa
            for pa in self.projectiles_adversaires
            if not pa.est_sorti
        ]

        # Vérification si on déclanche l'alerte ou la retire.
        if any(
            adv.rect.bottom >= self.config.axe_y_avertissement
            for adv in self.formation_adversaires.adversaires
        ):        
            self.defaite_imminente = True
        else:
            self.defaite_imminente = False
            
        # Vérification si adversaire a atteint la ligne de défaite
        if any(
            adv.rect.bottom >= self.config.axe_y_defaite
            for adv in self.formation_adversaires.adversaires
        ):        
            self.etat = EtatJeu.DEFAITE

        # Vérification si un projectile d'un adversaire a atteint le joueur.
        if self._gerer_collisions_joueur() is True:
            self.nombre_vies -= 1
            
            if self.nombre_vies <= 0:
                self.etat = EtatJeu.DEFAITE
            else: 
                self.clignotement_joueur_touche.reinitialiser()
                self.duree_clignotement_joueur_touche.reinitialiser()
                self.etat = EtatJeu.TOUCHE

        # Si tous les adversaires sont éliminés c'est une victoire.
        if self.formation_adversaires.nombre_adversaires == 0:
            self.etat = EtatJeu.VICTOIRE
            self.vitesse_formation_adversaires += \
                self.config.increment_vitesse_formation_adversaires

    def _mettre_a_jour_effets_visuels(self) -> None:
        """
        Met à jour les effets visuels temporaires et retire ceux qui sont terminés.
        """

        for effet in self.effets_visuels:
            effet.mettre_a_jour()

        self.effets_visuels = [
            effet
            for effet in self.effets_visuels
            if not effet.est_terminee
        ]

    def _dessiner(self) -> None:
        """
        Dessine la scène complète.
        """

        self.surface_jeu.blit(self.image_fond, (0, 0))
        temps_actuel = pygame.time.get_ticks()

        if self._joueur_doit_etre_dessine(temps_actuel):
            self.joueur.dessiner(self.surface_jeu)

        if self.projectile_joueur is not None:
            self.projectile_joueur.dessiner(self.surface_jeu)

        self._dessiner_effets_visuels()

        for pa in self.projectiles_adversaires:
            pa.dessiner(self.surface_jeu)

        if self.etat is EtatJeu.PREPARATION:
            rect = self.afficheur_texte.dessiner(
                self.config.titre,
                50,
                40,
                self.config.taille_police_titre,
            )
            self.afficheur_texte.dessiner(
                "Appuyez ESPACE pour démarrer",
                50,
                40,
                decalage_y_px=rect.height + 10
            )
        elif self.etat is EtatJeu.APPROCHE:
            self.animation_approche_adversaires.dessiner(
                self.surface_jeu,
                self.formation_adversaires,
            )
        elif self.etat is EtatJeu.VICTOIRE:
            rect = self.afficheur_texte.dessiner(
                "Bravo!",
                50,
                40,
                self.config.taille_police_titre,
            )
            self.afficheur_texte.dessiner(
                "Appuyez ESPACE pour continuer",
                50,
                40,
                decalage_y_px=rect.height + 10
            )
        elif self.etat is EtatJeu.DEFAITE:
            rect = self.afficheur_texte.dessiner(
                "Vous avez perdu!",
                50,
                40,
                self.config.taille_police_titre,
            )
            self.afficheur_texte.dessiner(
                "Appuyez ESPACE pour une nouvelle partie",
                50,
                40,
                decalage_y_px=rect.height + 10
            )
        else:
            self.formation_adversaires.dessiner(self.surface_jeu)

        # Dessine le pointage et les vies
        self.afficheur_texte.dessiner(str(self.pointage), 50, 98, self.config.taille_police_texte)
        texte = f"Vaisseaux : {self.nombre_vies}"
        self.afficheur_texte.dessiner(texte, 98, 98, self.config.taille_police_base)

        # Dessiner l'axe de défaite, il restera affiché jusqu'à une défaite ou victoire.
        if (
            self.etat is EtatJeu.EXECUTION
            and self.defaite_imminente
        ):
            if self.clignotement_defaut.est_visible(temps_actuel):
                pygame.draw.line(
                    self.surface_jeu,
                    self.config.couleur_axe_defaite,
                    (self.config.limite_x_min_zone_jouable, self.config.axe_y_defaite),
                    (self.config.limite_x_max_zone_jouable, self.config.axe_y_defaite),
                )
                self.afficheur_texte.dessiner(
                    "ALERTE : invasion imminente!",
                    50,
                    0,
                    self.config.taille_police_texte,
                    self.config.couleur_axe_defaite,
                    self.config.axe_y_defaite - 30)

        # Affiche la surface du jeu sans étirement avec des bords noir au besoin
        self.surface_affichage.fill((0, 0, 0))

        if self.zone_affichage.size == self.surface_jeu.get_size():
            self.surface_affichage.blit(self.surface_jeu, self.zone_affichage)
        else:
            image_redimensionnee = pygame.transform.scale(
                self.surface_jeu,
                self.zone_affichage.size,
            )
            self.surface_affichage.blit(image_redimensionnee, self.zone_affichage)

        pygame.display.flip()

    def _dessiner_effets_visuels(self) -> None:
        """
        Dessine les effets visuels temporaires.
        """

        for effet in self.effets_visuels:
            effet.dessiner(self.surface_jeu)

    def _charger_sons(self) -> None:
        """
        Chargement de tous les sons du jeux dans un dictionnaire.
        """
        
        self.sons = {
            "projectile_joueur": pygame.mixer.Sound(self.config.son_projectile_joueur),
            "projectile_adversaire": pygame.mixer.Sound(self.config.son_projectile_adversaire),
            "explosion_joueur": pygame.mixer.Sound(self.config.son_explosion_joueur),
            "explosion_adversaire": pygame.mixer.Sound(self.config.son_explosion_adversaire),
        }

    def _charger_image_fond(self) -> pygame.Surface:
        """
        Charge l'image de fond et l'adapte à la surface logique du jeu.
        """

        image_fond = pygame.image.load(self.config.image_fond_ecran).convert()
        return pygame.transform.smoothscale(
            image_fond,
            (self.config.largeur_fenetre, self.config.hauteur_fenetre),
        )

    def _demarrer_nouvelle_partie(self) -> None:
        """
        Démarre une nouvelle partie
        """

        self.nombre_vies = self.config.nb_vies_initiales
        self.pointage = 0
        self.vitesse_formation_adversaires = self.config.vitesse_initiale_formation_adversaires
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

        self._demarrer_nouveau_tableau()

    def _demarrer_nouveau_tableau(self) -> None:
        """
        Initialise un nouveau tableau que ce soit pour le début d'une partie ou en cours d'une
        partie après avoir vaincu un tableau
        """

        self.touche_tir_precedente = False
        self.defaite_imminente = False 
        self.projectile_joueur = None
        self.projectiles_adversaires = []
        self.effets_visuels = []

        duree_tir = self.config.delai_tir_adversaires_initial + \
            self.config.increment_delai_tir_adversaires
        self.tir_adversaires.changer_duree(duree_tir)

        self.clignotement_defaut.reinitialiser()
        self.formation_adversaires.creer_adversaires(self.vitesse_formation_adversaires)
        self.animation_approche_adversaires.demarrer(self.formation_adversaires)

    def _reprendre_apres_touche(self) -> None:
        """
        Reprise après avoir été touché par un projectile adversaire.
        """

        self.projectile_joueur = None
        self.projectiles_adversaires = []
        self.touche_tir_precedente = False

    def _joueur_doit_etre_dessine(self, temps_actuel: int) -> bool:
        """
        Indique si le joueur doit être dessiné selon l'état courant du jeu.
        """

        if self.etat is EtatJeu.DEFAITE:
            return False

        if self.etat is EtatJeu.TOUCHE:
            return self.clignotement_joueur_touche.est_visible(temps_actuel)

        return True
    
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

    def _tirer_projectile_joueur(self) -> None:
        """
        Crée un projectile joueur s'il n'y en a pas déjà un actif.
        """

        if self.projectile_joueur is not None:
            return

        self.sons["projectile_joueur"].play()

        x_centre_projectile = self.joueur.rect.centerx
        y_haut_projectile = self.joueur.rect.top
        centre_flash = (x_centre_projectile, y_haut_projectile)

        self.effets_visuels.append(FlashTir(centre_flash, self.config))

        self.projectile_joueur = ProjectileJoueur(
            x_centre_projectile,
            y_haut_projectile,
            self.config,
        )

    def _gerer_collisions_adversaires(self) -> None:
        """
        Gère les collisions d'un projectile du joueur avec les adversaires
        """
        
        if self.projectile_joueur is not None:
            adv = self.formation_adversaires.verifier_collision(self.projectile_joueur.rect)

            if adv is not None:
                self.effets_visuels.append(Explosion(adv.rect.center, self.config))
                self.sons["explosion_adversaire"].play()
                self.formation_adversaires.adversaires.remove(adv)
                self.projectile_joueur = None
                self.pointage += self.config.points_par_adversaire

    def _gerer_collisions_joueur(self) -> bool:
        """
        Gère les collisions des projectiles adversaire avec le joueur. 
        S'assure de retirer le projectile de la liste s'il y a collision.
        Retour : true si collision.
        """

        nb_projectiles_avant = len(self.projectiles_adversaires)

        self.projectiles_adversaires = [
            pa
            for pa in self.projectiles_adversaires
            if not self.joueur.verifier_collision(pa.rect)
        ]

        collision = False
        if len(self.projectiles_adversaires) != nb_projectiles_avant:
            self.sons["explosion_joueur"].play()
            collision = True

        return collision

if __name__ == "__main__":
    jeu = Jeu()
    jeu.executer()
