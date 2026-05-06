"""
Programme principal du jeu Space Devastator Solo
"""

import math
import os
import sys
import pygame

import niveaux

from array import array
from configparser import ConfigParser

from config import Configuration
from chemins import chemin_ancien_config_projet, chemin_config_utilisateur, chemin_ressource
from etats import EtatJeu, DirectionHorizontale
from commun import Minuteur, Clignotement, AfficheurTexte
from effets import EffetVisuel, Explosion, FlashTir
from objets import (
    Joueur,
    FormationAdversaires,
    AnimationApprocheAdversaires,
    ProjectileJoueur,
    GestionTirAdversaires,
    GestionAdversaireBonus,
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

        # Configuration initiale du jeu
        self.config = Configuration()
        self.rep_config = chemin_config_utilisateur()
        self.fichier_config = self._charger_fichier_config()
        self.pointage_record = self.fichier_config.getint("pointage", "record", fallback=0)

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
        self.image_vie = self._charger_image_vie()
        self.images_intro_adversaires = self._charger_images_intro_adversaires()

        self.sons = {
            "projectile_joueur": pygame.mixer.Sound(
                chemin_ressource(self.config.son_projectile_joueur)
            ),
            "projectile_adversaire": pygame.mixer.Sound(
                chemin_ressource(self.config.son_projectile_adversaire)
            ),
            "explosion_joueur": pygame.mixer.Sound(
                chemin_ressource(self.config.son_explosion_joueur)
            ),
            "explosion_adversaire": pygame.mixer.Sound(
                chemin_ressource(self.config.son_explosion_adversaire)
            ),
            "adversaire_bonus": pygame.mixer.Sound(
                chemin_ressource(self.config.son_adversaire_bonus)
            ),
            "victoire": pygame.mixer.Sound(
                chemin_ressource(self.config.son_victoire)
            ),
            "vie_bonus": pygame.mixer.Sound(
                chemin_ressource(self.config.son_vie_bonus)
            ),
        }
        self.sons_bonus: dict[int, pygame.mixer.Sound] = {}

        pygame.display.set_caption(self.config.titre)

        self.horloge = pygame.time.Clock()
        self.duree_clignotement_joueur_touche = Minuteur(
            self.config.duree_clignotement_joueur_touche_ms
        )

        self.joueur = Joueur(self.config)
        self.formation_adversaires = FormationAdversaires(self.config)
        self.animation_approche_adversaires = AnimationApprocheAdversaires(self.config)

        self.projectile_joueur: ProjectileJoueur | None = None
        self.effets_visuels: list[EffetVisuel] = []
        
        self.clignotement_defaut = Clignotement(self.config.freq_clignotement_defaut_ms)
        self.clignotement_joueur_touche = Clignotement(
            self.config.freq_clignotement_joueur_touche_ms
        )

        self.gestion_tir_adversaires = GestionTirAdversaires(
            self.sons["projectile_adversaire"],
            self.config
        )
        self.gestion_adversaire_bonus = GestionAdversaireBonus(
            self.sons["adversaire_bonus"],
            self.config,
        )

        # Objet utilitaire pour afficher du texte à l'écran.
        self.afficheur_texte = AfficheurTexte(
            self.surface_jeu,
            self.config.taille_police_texte,
            self.config.couleur_texte,
        )

        self.gestionnaire_niveaux = niveaux.GestionnaireNiveaux(niveaux.NIVEAUX)
        self.niveau_victoire = 0
        self.bonus_victoire = 0
        self.pointage_depart_bonus = 0
        self.pointage_cible_bonus = 0
        self.instant_depart_bonus = 0
        self.prochaine_tranche_son_bonus = 0
        self.derniere_tranche_vie_bonus = 0
        self.animation_bonus_terminee = True

        self.derniere_pos_x_projectile_joueur = 0
        self.minuteur_perte_projectile = Minuteur(250)

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

        self.fichier_config["pointage"]["record"] = str(self.pointage_record)        
        self._enregistrer_fichier_config()
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
                        self.etat is EtatJeu.VICTOIRE_NIVEAU
                        or self.etat is EtatJeu.PREPARATION
                    ):
                        if self._terminer_animation_bonus_si_necessaire():
                            continue
                        self._demarrer_nouveau_niveau()
                        self.etat = EtatJeu.APPROCHE
                    elif (
                        self.etat is EtatJeu.DEFAITE
                        or self.etat is EtatJeu.VICTOIRE_FINALE
                    ):
                        if self._terminer_animation_bonus_si_necessaire():
                            continue
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
                self.etat = EtatJeu.EXECUTION
            return

        if (
            self.etat is EtatJeu.TOUCHE 
            and self.duree_clignotement_joueur_touche.est_termine
        ):
           self._reprendre_apres_touche()
           self.etat = EtatJeu.EXECUTION

        if (
            self.etat is EtatJeu.VICTOIRE_NIVEAU
            or self.etat is EtatJeu.VICTOIRE_FINALE
        ):
            self._mettre_a_jour_bonus_victoire()
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

        # JALON important - Au delà de ce point le traitement n'est que pour le mode EXECUTION
        if self.etat is not EtatJeu.EXECUTION:
            return

        self.gestion_adversaire_bonus.mettre_a_jour(self.formation_adversaires)

        # Gestion du bouton de tir
        touche_tir = touches[pygame.K_a]
        if touche_tir and not self.touche_tir_precedente:
            self._tirer_projectile_joueur()
        self.touche_tir_precedente = touche_tir

        # Gestion du projectile du joueur
        if self.projectile_joueur is not None:
            self.projectile_joueur.mettre_a_jour()
            self._gerer_collisions_adversaires()
            self._gerer_collisions_adversaire_bonus()
            if self.projectile_joueur is not None and self.projectile_joueur.est_sorti:
                self.minuteur_perte_projectile.demarrer()
                self.tirs_perdus += 1
                self._modifier_pointage(self.config.points_projectile_perdu)
                self.derniere_pos_x_projectile_joueur = self.projectile_joueur.rect.centerx
                self.projectile_joueur = None

        self.gestion_tir_adversaires.mettre_a_jour(self.formation_adversaires)

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
        if self.gestion_tir_adversaires.verifier_collision(self.joueur) is True:
            self.sons["explosion_joueur"].play()
            self.nombre_vies -= 1
            
            if self.nombre_vies <= 0:
                self.etat = EtatJeu.DEFAITE
            else: 
                self.clignotement_joueur_touche.reinitialiser()
                self.duree_clignotement_joueur_touche.reinitialiser()
                self.projectile_joueur = None
                self.gestion_tir_adversaires.projectiles.clear()
                self.effets_visuels.clear()
                self.etat = EtatJeu.TOUCHE

        # Si tous les adversaires sont éliminés c'est une victoire.
        if self.formation_adversaires.nombre_adversaires == 0:
            niveau_termine = self.gestionnaire_niveaux.niveau_courant.numero
            self.projectile_joueur = None
            self.gestion_tir_adversaires.projectiles.clear()
            self.effets_visuels.clear()
            if self.gestionnaire_niveaux.passer_au_niveau_suivant():
                self.etat = EtatJeu.VICTOIRE_NIVEAU
            else:
                self.sons["victoire"].play()
                self.etat = EtatJeu.VICTOIRE_FINALE
            self._demarrer_bonus_victoire(niveau_termine)

        self._mettre_a_jour_pointage_record()
                
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

        # Affiche la perte de pointage pendant quelques temps si projectile du joueur est sorti
        if self.minuteur_perte_projectile.est_actif:
            police = pygame.font.Font(None, self.config.taille_police_pointage_explosion)
            surface_txt = police.render(
                str(self.config.points_projectile_perdu),
                True,
                self.config.couleur_pointage_negatif
            )
            pos = self.derniere_pos_x_projectile_joueur - 15, self.config.limite_y_min_zone_jouable
            self.surface_jeu.blit(surface_txt, pos)
            if self.minuteur_perte_projectile.est_termine:
                self.minuteur_perte_projectile.arreter()


        self._dessiner_effets_visuels()

        self.gestion_tir_adversaires.dessiner(self.surface_jeu)

        if self.etat is EtatJeu.PREPARATION:
            self._dessiner_ecran_preparation(temps_actuel)
        elif self.etat is EtatJeu.APPROCHE:
            self.animation_approche_adversaires.dessiner(
                self.surface_jeu,
                self.formation_adversaires,
            )
        elif self.etat is EtatJeu.VICTOIRE_NIVEAU:
            rect = self.afficheur_texte.dessiner(
                f"Niveau {self.niveau_victoire} réussi !",
                50,
                20,
                self.config.taille_police_titre,
            )
            rect = self._dessiner_bonus_victoire()
            self.afficheur_texte.dessiner(
                "Appuyez ESPACE pour continuer",
                50,
                70,
            )
        elif self.etat is EtatJeu.VICTOIRE_FINALE:
            rect = self.afficheur_texte.dessiner(
                f"VICTOIRE ! Niveau {self.niveau_victoire} réussi !",
                50,
                15,
                self.config.taille_police_titre,
            )
            rect = self.afficheur_texte.dessiner(
                "Vous avez repoussé tous les envahisseurs !",
                50,
                rect,
                self.config.taille_police_titre - 16,
            )
            rect = self._dessiner_bonus_victoire()
            self.afficheur_texte.dessiner(
                "Appuyez ESPACE pour une nouvelle partie",
                50,
                70,
            )
        elif self.etat is EtatJeu.DEFAITE:
            rect = self.afficheur_texte.dessiner(
                "Les envahisseurs se sont emparés de la Terre !",
                50,
                40,
                self.config.taille_police_titre,
            )
            self.afficheur_texte.dessiner(
                "Appuyez ESPACE pour une nouvelle partie",
                50,
                70,
            )
        else:
            self.formation_adversaires.dessiner(self.surface_jeu)
            self.gestion_adversaire_bonus.dessiner(self.surface_jeu)

        # Dessine le pointage et les vies
        texte = f"{str(self.pointage)}"
        self.afficheur_texte.dessiner(
            texte, 2, 2, self.config.taille_police_texte, self.config.couleur_pointage)
        
        texte = f"Record: {str(self.pointage_record)}"
        self.afficheur_texte.dessiner(
            texte, 98, 2, self.config.taille_police_texte, self.couleur_pointage)
        
        if self.etat is EtatJeu.EXECUTION or self.etat is EtatJeu.TOUCHE:
            texte = f"Niveau {str(self.gestionnaire_niveaux.niveau_courant.numero)}"
            self.afficheur_texte.dessiner(texte, 2, 98, self.config.taille_police_base)
        
        # Affiche des minis vaisseaux pour chaque vie
        position_x_vies = round(self.surface_jeu.get_width() * 98 / 100)
        position_y_vies = round(self.surface_jeu.get_height() * 98 / 100)
        largeur_vie = self.image_vie.get_width()
        espacement_vies = 6

        for index_vie in range(self.nombre_vies):
            decalage_x = index_vie * (largeur_vie + espacement_vies)
            rect_image_vie = self.image_vie.get_rect(
                bottomright=(position_x_vies - decalage_x, position_y_vies)
            )
            self.surface_jeu.blit(self.image_vie, rect_image_vie)

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
                pct_y_alerte = round(
                    (self.config.axe_y_defaite - 10)
                    * 100
                    / self.surface_jeu.get_height()
                )
                self.afficheur_texte.dessiner(
                    "ALERTE : invasion imminente!",
                    50,
                    pct_y_alerte,
                    self.config.taille_police_texte,
                    self.config.couleur_axe_defaite,
                )

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

    def _dessiner_ecran_preparation(self, temps_actuel: int) -> None:
        """
        Affiche l'écran d'introduction avant le début de la partie.
        """

        marge_x = 110
        marge_y = 60
        largeur = self.config.largeur_fenetre - marge_x * 2
        hauteur = 560
        rect_panneau = pygame.Rect(marge_x, marge_y, largeur, hauteur)

        voile = pygame.Surface(rect_panneau.size, pygame.SRCALPHA)
        voile.fill((5, 12, 28, 205))
        self.surface_jeu.blit(voile, rect_panneau)

        pygame.draw.rect(
            self.surface_jeu,
            self.config.couleur_pointage,
            rect_panneau,
            width=2,
            border_radius=8,
        )
        pygame.draw.rect(
            self.surface_jeu,
            self.config.couleur_bonus,
            rect_panneau.inflate(-18, -18),
            width=1,
            border_radius=6,
        )

        rect_titre = self.afficheur_texte.dessiner(
            self.config.titre.upper(),
            50,
            14,
            self.config.taille_police_titre + 10,
            self.config.couleur_bonus,
        )
        self.afficheur_texte.dessiner(
            f"Mission : survivre aux {len(niveaux.NIVEAUX)} niveaux",
            50,
            rect_titre,
            self.config.taille_police_texte + 6,
        )

        self._dessiner_visuel_preparation(temps_actuel, rect_panneau)

        x_gauche = rect_panneau.left + 60
        x_droite = rect_panneau.centerx + 35
        y_depart = rect_panneau.top + 185
        interligne = 34

        self._dessiner_titre_section_intro("Objectif", x_gauche, y_depart)
        self._dessiner_ligne_intro(
            "Détruire toutes les formations ennemies",
            x_gauche,
            y_depart + 38,
        )
        self._dessiner_ligne_intro(
            "Ne pas laisser les adversaires atteindre la ligne d'invasion",
            x_gauche,
            y_depart + 38 + interligne,
        )

        self._dessiner_titre_section_intro("Commandes", x_droite, y_depart)
        self._dessiner_ligne_intro(
            "Flèches gauche/droite : déplacer",
            x_droite,
            y_depart + 38,
        )
        self._dessiner_ligne_intro(
            "A : tirer un projectile",
            x_droite,
            y_depart + 38 + interligne,
        )
        self._dessiner_ligne_intro(
            "Échap : quitter la partie",
            x_droite,
            y_depart + 38 + interligne * 2,
        )

        y_bas = rect_panneau.top + 320
        self._dessiner_titre_section_intro("Bonus", x_gauche, y_bas)
        self._dessiner_ligne_intro(
            "Soucoupe jaune : une visite par niveau pair",
            x_gauche,
            y_bas + 38,
            self.config.couleur_bonus,
        )
        self._dessiner_ligne_intro(
            "Fin de niveau : vies restantes x 250 x précision",
            x_gauche,
            y_bas + 38 + interligne,
            self.config.couleur_bonus,
        )
        self._dessiner_ligne_intro(
            "Multiplicateur selon précision obtenue",
            x_gauche,
            y_bas + 38 + interligne * 2,
            self.config.couleur_bonus,
        )
        self._dessiner_ligne_intro(
            f"Vaisseau supplémentaire à chaque"
            f" {self.config.tranche_points_vie_supplementaire} points",
            x_gauche,
            y_bas + 38 + interligne * 3,
            self.config.couleur_bonus,
        )

        y_bas = y_bas + 32
        self._dessiner_titre_section_intro("Pénalités", x_droite, y_bas)
        self._dessiner_ligne_intro(
            "Tir perdu : 100 points en moins et bonus réduit",
            x_droite,
            y_bas + 38,
            self.config.couleur_pointage_negatif,
        )
        self._dessiner_ligne_intro(
            "Impact projectile ennemi : perte de vaisseau",
            x_droite,
            y_bas + 38 + interligne,
            self.config.couleur_pointage_negatif,
        )
        self._dessiner_ligne_intro(
            "Invasion ou perte de tous les vaisseaux : fin de partie",
            x_droite,
            y_bas + 38 + interligne * 2,
            self.config.couleur_pointage_negatif,
        )

        if self.clignotement_defaut.est_visible(temps_actuel):
            self.afficheur_texte.dessiner(
                "Appuyez ESPACE pour lancer le niveau 1",
                50,
                74,
                self.config.taille_police_texte + 6,
                self.config.couleur_texte,
            )

    def _dessiner_visuel_preparation(
        self,
        temps_actuel: int,
        rect_panneau: pygame.Rect,
    ) -> None:
        """
        Dessine une petite scène arcade avec les sprites du jeu.
        """

        marge_interne = 48
        positions = (
            (
                rect_panneau.left + marge_interne,
                rect_panneau.top + marge_interne,
            ),
            (
                rect_panneau.right - marge_interne,
                rect_panneau.top + marge_interne,
            ),
            (
                rect_panneau.left + marge_interne,
                rect_panneau.bottom - marge_interne,
            ),
            (
                rect_panneau.right - marge_interne,
                rect_panneau.bottom - marge_interne,
            ),
        )

        for index, (image, position) in enumerate(
            zip(self.images_intro_adversaires, positions)
        ):
            decalage_y = round(
                math.sin(temps_actuel * 0.005 + index) * 5
            )
            rect_adversaire = image.get_rect(
                center=(position[0], position[1] + decalage_y)
            )
            self.surface_jeu.blit(image, rect_adversaire)

    def _dessiner_titre_section_intro(self, texte: str, x: int, y: int) -> None:
        """
        Dessine un titre de section pour l'écran d'introduction.
        """

        police = pygame.font.Font(None, self.config.taille_police_texte + 12)
        surface_txt = police.render(texte.upper(), True, self.config.couleur_pointage)
        self.surface_jeu.blit(surface_txt, (x, y))

    def _dessiner_ligne_intro(
        self,
        texte: str,
        x: int,
        y: int,
        couleur: tuple[int, int, int] | None = None,
    ) -> None:
        """
        Dessine une ligne d'information avec une puce lumineuse.
        """

        couleur_texte = couleur if couleur is not None else self.config.couleur_texte
        pygame.draw.circle(self.surface_jeu, couleur_texte, (x + 8, y + 10), 4)

        police = pygame.font.Font(None, self.config.taille_police_texte + 2)
        surface_txt = police.render(texte, True, couleur_texte)
        self.surface_jeu.blit(surface_txt, (x + 24, y))

    def _charger_image_fond(self) -> pygame.Surface:
        """
        Charge l'image de fond et l'adapte à la surface logique du jeu.
        """

        image_fond = pygame.image.load(
            chemin_ressource(self.config.image_fond_ecran)
        ).convert()
        return pygame.transform.smoothscale(
            image_fond,
            (self.config.largeur_fenetre, self.config.hauteur_fenetre),
        )

    def _charger_image_vie(self) -> pygame.Surface:
        """
        Charge l'icône du joueur affichée à côté du nombre de vies.
        """

        image_vie = pygame.image.load(
            chemin_ressource(self.config.image_joueur)
        ).convert_alpha()
        return pygame.transform.smoothscale(image_vie, (32, 32))

    def _charger_images_intro_adversaires(self) -> list[pygame.Surface]:
        """
        Charge les sprites d'adversaires utilisés par l'écran de préparation.
        """

        return [
            pygame.transform.smoothscale(
                pygame.image.load(
                    chemin_ressource(chemin_image)
                ).convert_alpha(),
                (self.config.largeur_adversaire, self.config.hauteur_adversaire),
            )
            for chemin_image in self.config.image_adversaires
        ]

    def _demarrer_nouvelle_partie(self) -> None:
        """
        Démarre une nouvelle partie
        """

        self.nombre_vies = self.config.nb_vies_initiales
        self.pointage = 0
        self.derniere_tranche_vie_bonus = 0
        self.couleur_pointage = self.config.couleur_pointage
        self.gestionnaire_niveaux.recommencer()

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

        self._demarrer_nouveau_niveau()

    def _demarrer_nouveau_niveau(self) -> None:
        """
        Initialise un nouveau niveau que ce soit pour le début d'une partie ou en cours d'une
        partie après avoir vaincu un niveau
        """

        self.tirs_perdus = 0
        self.touche_tir_precedente = False
        self.defaite_imminente = False 
        self.projectile_joueur = None
        self.effets_visuels.clear()
        self.clignotement_defaut.reinitialiser()

        # On obtiens un ParametresNiveau dans la liste selon le niveau courant puis on initialise
        # nos différents objets à partir de ces paramètres
        params = self.gestionnaire_niveaux.niveau_courant
        self.gestion_tir_adversaires.initialiser(params.nb_canaux_tir)
        self.gestion_adversaire_bonus.initialiser(
            params.adversaire_bonus_actif,
            params.vitesse_adversaire_bonus,
            params.delai_min_adversaire_bonus_ms,
            params.delai_max_adversaire_bonus_ms,
        )
        self.formation_adversaires.creer_adversaires(
            params.vitesse_formation_adversaires,
            params.colonnes_adversaires,
            params.lignes_adversaires,
            params.espacement_adversaire_x,
            params.espacement_adversaire_y,
        )

        # On joue l'animation de début de niveau
        self.animation_approche_adversaires.demarrer(self.formation_adversaires)

    def _reprendre_apres_touche(self) -> None:
        """
        Reprise après avoir été touché par un projectile adversaire.
        """

        self.projectile_joueur = None
        self.gestion_tir_adversaires.initialiser(
            self.gestionnaire_niveaux.niveau_courant.nb_canaux_tir
        )
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

    def _demarrer_bonus_victoire(self, niveau_termine: int) -> None:
        """
        Prépare le bonus accordé à la fin d'un niveau.
        """

        self.niveau_victoire = niveau_termine
        self.bonus_victoire = (
            self.nombre_vies
            * self.config.points_bonus_vie_par_niveau
            * self._calculer_multiplicateur_bonus()
        )
        self.pointage_depart_bonus = self.pointage
        self.pointage_cible_bonus = self.pointage + self.bonus_victoire
        self.instant_depart_bonus = pygame.time.get_ticks()
        self.prochaine_tranche_son_bonus = self.config.tranche_son_bonus
        self.animation_bonus_terminee = self.bonus_victoire <= 0

        if self.animation_bonus_terminee:
            self._definir_pointage(self.pointage_cible_bonus)

    def _mettre_a_jour_bonus_victoire(self) -> None:
        """
        Anime le pointage jusqu'au total incluant le bonus de victoire.
        """

        if self.animation_bonus_terminee:
            return

        temps_ecoule = pygame.time.get_ticks() - self.instant_depart_bonus
        nb_tranches_affichees = (
            temps_ecoule // self.config.duree_tranche_bonus_ms
        )

        points_bonus_affiches = min(
            nb_tranches_affichees * self.config.tranche_son_bonus,
            self.bonus_victoire,
        )
        self._definir_pointage(self.pointage_depart_bonus + points_bonus_affiches)

        while self.prochaine_tranche_son_bonus <= points_bonus_affiches:
            index_son = (
                self.prochaine_tranche_son_bonus
                // self.config.tranche_son_bonus
            )
            self._jouer_son_bonus(index_son)
            self.prochaine_tranche_son_bonus += self.config.tranche_son_bonus

        if points_bonus_affiches >= self.bonus_victoire:
            self._definir_pointage(self.pointage_cible_bonus)
            self.animation_bonus_terminee = True

    def _terminer_animation_bonus_si_necessaire(self) -> bool:
        """
        Termine immédiatement l'animation si le joueur appuie pendant le décompte.

        Retourne True si l'appui a été utilisé pour accélérer l'animation.
        """

        if self.animation_bonus_terminee:
            return False

        self._definir_pointage(self.pointage_cible_bonus)
        self.animation_bonus_terminee = True

        return True

    def _modifier_pointage(self, points: int) -> None:
        """
        Modifie le pointage et applique les effets associés au nouveau total.
        """

        self._definir_pointage(self.pointage + points)

    def _definir_pointage(self, nouveau_pointage: int) -> None:
        """
        Définit le pointage et vérifie les vies bonus et le record.
        """

        self.pointage = nouveau_pointage
        self._attribuer_vies_bonus_si_necessaire()
        self._mettre_a_jour_pointage_record()

    def _attribuer_vies_bonus_si_necessaire(self) -> None:
        """
        Donne une vie supplémentaire pour chaque nouvelle tranche de points atteinte.
        """

        tranche_points = self.config.tranche_points_vie_supplementaire

        if tranche_points <= 0:
            return

        tranche_atteinte = max(0, self.pointage // tranche_points)

        if tranche_atteinte <= self.derniere_tranche_vie_bonus:
            return

        nb_vies_bonus = tranche_atteinte - self.derniere_tranche_vie_bonus

        for _ in range(nb_vies_bonus):
            self.nombre_vies += 1
            self.sons["vie_bonus"].play()

        self.derniere_tranche_vie_bonus = tranche_atteinte

    def _mettre_a_jour_pointage_record(self) -> None:
        """
        Met à jour le record si le pointage courant le dépasse.
        """

        if self.pointage > self.pointage_record:
            self.pointage_record = self.pointage
            self.couleur_pointage = self.config.couleur_pointage_record

    def _dessiner_bonus_victoire(self) -> pygame.Rect:
        """
        Affiche le détail du pointage et du bonus sur les écrans de victoire.
        """

        rect = self.afficheur_texte.dessiner(
            f"Pointage : {self.pointage_depart_bonus}",
            50,
            35,
            self.config.taille_police_texte + 8
        )

        multiplicateur_bonus = self._calculer_multiplicateur_bonus()
        
        if multiplicateur_bonus == 5:
            texte_bonus = "Aucun tir perdu. Bonus x 5"
        elif multiplicateur_bonus == 3:
            texte_bonus = "Moins de 5 tirs perdus. Bonus x 3"
        elif multiplicateur_bonus == 2:
            texte_bonus = "Seulement 6 à 10 tirs perdus. Bonus x 2"
        else:
            texte_bonus = f"{self.tirs_perdus} tirs perdus. Bonus x 1"

        rect = self.afficheur_texte.dessiner(
            texte_bonus,
            50,
            rect,
            self.config.taille_police_texte - 4,
        )

        rect = self.afficheur_texte.dessiner(
            f"---------------------------------------------------",
            50,
            rect,
        )

        rect = self.afficheur_texte.dessiner(
            f"Bonus : {self.nombre_vies}"
            f" x {self.config.points_bonus_vie_par_niveau}"
            f" x {multiplicateur_bonus}" 
            f" = {self.bonus_victoire}",
            50,
            rect,
            self.config.taille_police_texte + 8,
            self.config.couleur_bonus,
        )

        rect = self.afficheur_texte.dessiner(
            f"Total : {self.pointage}",
            50,
            rect,
            self.config.taille_police_titre,
            self.config.couleur_pointage,
        )

        return rect

    def _calculer_multiplicateur_bonus(self) -> int:
        """
        Calcule le multiplicateur de bonus
        """
        multiplicateur_bonus = 1
        if self.tirs_perdus == 0:
            multiplicateur_bonus = 5
        elif self.tirs_perdus < 5:
            multiplicateur_bonus = 3
        elif self.tirs_perdus < 10:
            multiplicateur_bonus = 2

        return multiplicateur_bonus

    def _jouer_son_bonus(self, index_son: int) -> None:
        """
        Joue un court son de bonus dont la hauteur monte progressivement.
        """

        son = self.sons_bonus.get(index_son)

        if son is None:
            son = self._creer_son_bonus(index_son)
            self.sons_bonus[index_son] = son

        son.play()

    def _creer_son_bonus(self, index_son: int) -> pygame.mixer.Sound:
        """
        Génère un court bip sans ajouter de fichier audio au projet.
        """

        frequence_mixeur, _, canaux = pygame.mixer.get_init()
        frequence_son = (
            self.config.frequence_son_bonus_depart
            + self.config.increment_frequence_son_bonus * index_son
        )
        nb_echantillons = int(
            frequence_mixeur * self.config.duree_son_bonus_ms / 1000
        )
        amplitude = 9000
        echantillons = array("h")

        for index_echantillon in range(nb_echantillons):
            temps = index_echantillon / frequence_mixeur
            valeur = int(amplitude * math.sin(math.tau * frequence_son * temps))

            for _ in range(canaux):
                echantillons.append(valeur)

        return pygame.mixer.Sound(buffer=echantillons)
    
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
                self.effets_visuels.append(
                    Explosion(adv.rect.center, adv.ValeurPointage, self.config)
                )
                self.sons["explosion_adversaire"].play()
                self.formation_adversaires.adversaires.remove(adv)
                self.projectile_joueur = None
                self._modifier_pointage(adv.ValeurPointage)

    def _gerer_collisions_adversaire_bonus(self) -> None:
        """
        Gère les collisions d'un projectile du joueur avec l'adversaire bonus
        """

        if self.projectile_joueur is not None:
            adv = self.gestion_adversaire_bonus.adversaire
            if adv is not None:
                points = self.gestionnaire_niveaux.niveau_courant.pointage_adversaire_bonus
                if adv.verifier_collision(self.projectile_joueur.rect):
                    self.gestion_adversaire_bonus.retirer_adversaire()
                    self.effets_visuels.append(
                        Explosion(adv.rect.center, points, self.config)
                    )
                    self.sons["explosion_adversaire"].play()
                    self.projectile_joueur = None
                    self._modifier_pointage(points)


    def _charger_fichier_config(self) -> ConfigParser:
        """
        Charge la configuration sauvegardée du jeu.
        """

        config_sds = ConfigParser()
        ancien_config = chemin_ancien_config_projet()

        if self.rep_config.exists():
            config_sds.read(self.rep_config, encoding="utf-8")
        elif ancien_config.exists() and ancien_config != self.rep_config:
            config_sds.read(ancien_config, encoding="utf-8")

        if not config_sds.has_section("pointage"):
            config_sds["pointage"] = {}

        if "record" not in config_sds["pointage"]:
            config_sds["pointage"]["record"] = "0"

        return config_sds

    def _enregistrer_fichier_config(self) -> None:
        """
        Enregistre la configuration sauvegardée du jeu.
        """

        self.rep_config.parent.mkdir(parents=True, exist_ok=True)

        with self.rep_config.open("w", encoding="utf-8") as fichier:
            self.fichier_config.write(fichier)

if __name__ == "__main__":
    jeu = Jeu()
    jeu.executer()
