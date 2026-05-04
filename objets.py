"""Objets principaux qui composent le jeu."""

import random
import math
import pygame

from config import Configuration
from etats import DirectionHorizontale
from commun import Minuteur


class Joueur:
    """Vaisseau contrôlé par le joueur."""

    def __init__(self, config: Configuration) -> None:
        """
        Constructeur
        """
        
        self.config = config
        largeur_zone_jouable = (
            config.limite_x_max_zone_jouable
            - config.limite_x_min_zone_jouable
        )
        x = (
            config.limite_x_min_zone_jouable
            + (largeur_zone_jouable - config.largeur_joueur) // 2
        )
        y = (config.limite_y_max_zone_jouable - config.hauteur_joueur)
        self.rect = pygame.Rect(
            x,
            y,
            config.largeur_joueur,
            config.hauteur_joueur,
        )

        self.image = pygame.image.load(self.config.image_joueur).convert_alpha()
        self.image = pygame.transform.smoothscale(
            self.image,
            (self.config.largeur_joueur, self.config.hauteur_joueur),
        )

    def dessiner(self, surface: pygame.Surface) -> None:
        """
        Dessine le joueur.
        """
    
        surface.blit(self.image, self.rect)
        #pygame.draw.rect(surface, self.config.couleur_joueur, self.rect)

    def deplacer(self, direction: DirectionHorizontale) -> None:
        """
        Deplace le joueur.
        """
        
        self.rect.x += direction * self.config.vitesse_joueur

        if self.rect.left < self.config.limite_x_min_zone_jouable:
            self.rect.left = self.config.limite_x_min_zone_jouable 
        
        if self.rect.right > self.config.limite_x_max_zone_jouable:
            self.rect.right = self.config.limite_x_max_zone_jouable

    def verifier_collision(self, rect: pygame.Rect) -> bool:
        """
        Vérfie s'il y a collision avec le rectangle passé en paramètre.
        """
        
        rect_reduit = self.rect.inflate(0, -60)

        return rect_reduit.colliderect(rect)


class ProjectileJoueur:
    """Projectile tiré par le joueur vers le haut."""

    def __init__(self, x_centre: int, y_haut: int, config: Configuration) -> None:
        """
        Constructeur
        """

        self.config = config
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
        """
        Indique si le projectile est sorti par le haut de l'écran.
        """
        
        return self.rect.bottom < self.limite_projectile_haut

    def mettre_a_jour(self) -> None:
        """
        Déplace le projectile vers le haut.
        """
        
        self.rect.y -= self.config.vitesse_projectile_joueur

    def dessiner(self, surface: pygame.Surface) -> None:
        """
        Dessine le projectile sous forme de rectangle.
        """
        
        pygame.draw.rect(
            surface,
            self.config.couleur_projectile_joueur,
            self.rect,
            border_radius=4,
        )

class Adversaire:
    """Adversaire individuel dans la grille."""

    VALEUR_POINTAGE = [100, 250, 500, 500] 

    def __init__(self, x: int, y: int, niveau: int, config: Configuration) -> None:
        """
        Constructeur
        """

        self.config = config
        self.rect = pygame.Rect(
            x,
            y,
            config.largeur_adversaire,
            config.hauteur_adversaire,
        )

        self.image = pygame.image.load(config.image_adversaires[niveau]).convert_alpha()
        self.image = pygame.transform.smoothscale(
            self.image,
            (config.largeur_adversaire, config.hauteur_adversaire),
        )

        self.phase_animation = random.uniform(0, math.tau)
        self.niveau_adv = niveau
        
    def dessiner(self, surface: pygame.Surface) -> None:
        """Dessine l'adversaire avec un léger flottement visuel."""

        temps = pygame.time.get_ticks()
        amplitude = self.config.amplitude_flottement_adversaire
        vitesse = self.config.vitesse_flottement_adversaire

        decalage_y = math.sin(temps * vitesse + self.phase_animation) * amplitude
        rect_affichage = self.rect.move(0, round(decalage_y))

        surface.blit(self.image, rect_affichage)

    @property
    def ValeurPointage(self) -> int:
        """
        Retourne la valeur en point de l'adversaire.
        """
        return (self.VALEUR_POINTAGE[self.niveau_adv])


class FormationAdversaires:
    """Gère le déplacement collectif des adversaires."""

    def __init__(self, config: Configuration) -> None:
        """
        Constructeur
        """
        
        self.config = config
        self.adversaires = []
        self.direction = DirectionHorizontale.DROITE

    @property
    def nombre_adversaires(self) -> int:
        """
        Retourne le nombre d'adversaires encore présents.
        """
        
        return len(self.adversaires)

    def creer_adversaires(self,
                          vitesse: int,
                          nb_colonnes: int,
                          nb_lignes: int,
                          espacement_x: int,
                          espacement_y: int,
        )-> None:
        """
        Initialise tous les adversaires à partir des infos de la configuration.
        """

        self.vitesse_formation = vitesse
        self.direction = DirectionHorizontale.DROITE
        self.adversaires = []

        pas_x = (
            self.config.largeur_adversaire
            + espacement_x
        )
        pas_y = (
            self.config.hauteur_adversaire
            + espacement_y
        )

        niveau_adv = nb_lignes - 1

        for lig in range(nb_lignes):
            for col in range(nb_colonnes):
                x = self.config.depart_adversaire_grille_x + col * pas_x
                y = self.config.depart_adversaire_grille_y + lig * pas_y
                self.adversaires.append(Adversaire(x, y, niveau_adv, self.config))
            niveau_adv -= 1

    def verifier_collision(self, rect: pygame.Rect) -> Adversaire | None:
        """
        Vérfie si un des adversaires est entré en collision avec le rectangle passé en
        paramètre. Si oui, retourne l'adversaire touché, sinon retourne None.
        """
        
        for adv in self.adversaires:
            rect_reduit = adv.rect.inflate(0, -30)
            if rect.colliderect(rect_reduit):
                return adv

        return None

    def trouver_tireurs_valides(self) -> list[Adversaire]:
        """
        Retourne les adversaires qui sont en première ligne dans leur colonne.
        """

        tireurs_par_colonne: dict[int, Adversaire] = {}

        for adv in self.adversaires:
            tireur_courant = tireurs_par_colonne.get(adv.rect.x)

            if tireur_courant is None or adv.rect.bottom > tireur_courant.rect.bottom:
                tireurs_par_colonne[adv.rect.x] = adv

        return list(tireurs_par_colonne.values())

    def mettre_a_jour(self) -> None:
        """
        Déplace la formation et la fait descendre lorsqu'elle touche un bord.
        """
        
        if not self.adversaires:
            return

        decalage_x = int(self.direction) * self.vitesse_formation

        bord_gauche = min(adv.rect.left for adv in self.adversaires)
        bord_droit = max(adv.rect.right for adv in self.adversaires)

        touche_bord_gauche = (
            bord_gauche + decalage_x <= self.config.limite_x_min_zone_jouable
        )
        touche_bord_droit = (
            bord_droit + decalage_x >= self.config.limite_x_max_zone_jouable
        )

        if touche_bord_gauche or touche_bord_droit:
            self.direction = DirectionHorizontale(-int(self.direction))

            for adv in self.adversaires:
                adv.rect.y += self.config.descente_formation_adversaires

            return

        for adv in self.adversaires:
            adv.rect.x += decalage_x

    def dessiner(self, surface: pygame.Surface) -> None:
        """
        Dessine tous les adversaires de la formation.
        """

        for adv in self.adversaires:
            adv.dessiner(surface)

class ProjectileAdversaire:
    """Projectile tiré par les Adversaires vers le bas."""

    def __init__(self, adv: Adversaire, config: Configuration) -> None:
        """
        Constructeur
        """

        self.config = config
        self.rect = pygame.Rect(
            0,
            0,
            config.largeur_projectile_adversaire,
            config.hauteur_projectile_adversaire,
        )
        self.rect.centerx = adv.rect.centerx
        self.limite_projectile_bas = config.limite_y_max_zone_jouable
        self.rect.bottom = adv.rect.bottom - config.hauteur_projectile_adversaire
        
    @property
    def est_sorti(self) -> bool:
        """
        Indique si le projectile est sorti par le bas de l'écran.
        """
        
        return self.rect.top > self.limite_projectile_bas

    def mettre_a_jour(self) -> None:
        """
        Déplace le projectile vers le bas.
        """
        
        self.rect.y += self.config.vitesse_projectile_adversaire

    def dessiner(self, surface: pygame.Surface) -> None:
        """
        Dessine temporairement le projectile sous forme de rectangle.
        """
        
        pygame.draw.rect(
            surface,
            self.config.couleur_projectile_adversaire,
            self.rect,
            border_radius=1,
        )

class AnimationApprocheAdversaires:
    """Anime l'arrivée des adversaires en les dessinant de plus en plus grands."""

    def __init__(self, config: Configuration) -> None:
        """
        Constructeur.
        """

        self.config = config
        self.instant_depart = 0
        self.adversaires_a_animer: list[Adversaire] = []
        self.index_adversaire = 0
        self.echelles_par_adversaire: dict[Adversaire, float] = {}

    def demarrer(self, formation_adversaires: FormationAdversaires) -> None:
        """
        Démarre l'animation d'approche.
        """

        self.instant_depart = pygame.time.get_ticks()

        self.adversaires_a_animer = formation_adversaires.adversaires.copy()
        random.shuffle(self.adversaires_a_animer)
        self.index_adversaire = 0
        self.echelles_par_adversaire = {
            adv: 0.0
            for adv in formation_adversaires.adversaires
        }

    def mettre_a_jour(self) -> bool:
        """
        Met à jour l'échelle courante de chaque adversaire.

        Retourne True lorsque l'animation est terminée.
        """

        duree_ms = self.config.duree_approche_adversaire_ms

        if duree_ms <= 0 or not self.adversaires_a_animer:
            self.echelles_par_adversaire = {
                adv: 1.0
                for adv in self.echelles_par_adversaire
            }
            return True

        if self.index_adversaire >= len(self.adversaires_a_animer):
            return True

        adversaire_courant = self.adversaires_a_animer[self.index_adversaire]
        temps_animation = pygame.time.get_ticks() - self.instant_depart
        echelle_depart = self.config.echelle_initiale_approche_adversaires
        progression = min(temps_animation / duree_ms, 1.0)
        echelle = echelle_depart + (1.0 - echelle_depart) * progression
        self.echelles_par_adversaire[adversaire_courant] = echelle

        if progression < 1.0:
            return False

        self.echelles_par_adversaire[adversaire_courant] = 1.0
        self.index_adversaire += 1
        self.instant_depart = pygame.time.get_ticks()

        return self.index_adversaire >= len(self.adversaires_a_animer)

    def dessiner(
        self,
        surface: pygame.Surface,
        formation_adversaires: FormationAdversaires,
    ) -> None:
        """
        Dessine les adversaires avec leur échelle courante.
        """

        for adv in formation_adversaires.adversaires:
            echelle = self.echelles_par_adversaire.get(adv, 1.0)

            if echelle <= 0.0:
                continue

            largeur = max(1, int(adv.rect.width * echelle))
            hauteur = max(1, int(adv.rect.height * echelle))
            image = pygame.transform.smoothscale(adv.image, (largeur, hauteur))
            rect = image.get_rect(center=adv.rect.center)
            surface.blit(image, rect)

class GestionTirAdversaires:
    """
    Permet de gérer les tirs de projectiles des adversaires.
    """

    VITESSE_TIR_INITIAL_MIN = 2500
    VITESSE_TIR_INITIAL_MAX = 3500
    INCREMENT_VITESSE_TIR = -500

    def __init__(self, son: pygame.mixer.Sound, config: Configuration) -> None:
        """
        Constructeur
        """

        self.son = son
        self.config = config
        self.projectiles: list[ProjectileAdversaire] = []
        self.minuteurs: list[Minuteur] = []

    def initialiser(self, nb_canaux: int) -> None:
        """
        Vide les projectiles et réinitialise pour reprendre une partie ou un niveau.
        """

        self.nb_canaux = nb_canaux
        self.minuteurs.clear()
        for index_minuteur in range(nb_canaux):
            duree = random.randint(
                self.VITESSE_TIR_INITIAL_MIN,
                self.VITESSE_TIR_INITIAL_MAX,
            )
            self.minuteurs.insert(index_minuteur, Minuteur(duree))

        self.projectiles.clear()

    def mettre_a_jour(self, formation: FormationAdversaires) -> None:
        """
        Déclenche les tirs adverses et met à jour les projectiles déjà actifs.
        """

        tireurs_valides = formation.trouver_tireurs_valides()
        nb_tirs_possibles = min(len(tireurs_valides), self.nb_canaux)

        if nb_tirs_possibles > 0:
            # random.sample peut choisir directement des objets dans une liste.
            tireurs_choisis = random.sample(tireurs_valides, nb_tirs_possibles)

            for index_tir in range(nb_tirs_possibles):
                if self.minuteurs[index_tir].est_termine():
                    tireur = tireurs_choisis[index_tir]

                    self.son.play()
                    self.projectiles.append(
                        ProjectileAdversaire(tireur, self.config)
                    )
                    self.minuteurs[index_tir].reinitialiser()

        for projectile in self.projectiles:
            projectile.mettre_a_jour()

        # On garde seulement les projectiles encore visibles dans la zone de jeu.
        projectiles_visibles = []
        for projectile in self.projectiles:
            if not projectile.est_sorti:
                projectiles_visibles.append(projectile)
        self.projectiles = projectiles_visibles

    def dessiner(self, surface: pygame.Surface) -> None:
        """
        Dessine l'ensemble des projectiles actifs sur la surface de jeu.
        """

        for projectile in self.projectiles:
            projectile.dessiner(surface)

    def verifier_collision(self, joueur: Joueur) -> bool:
        """
        Gère les collisions des projectiles avec le joueur. 
        S'assure de retirer le projectile de la liste s'il y a collision.
        Retour : true si collision.
        """

        nb_projectiles_avant = len(self.projectiles)

        self.projectiles = [
            projectile
            for projectile in self.projectiles
            if not joueur.verifier_collision(projectile.rect)
        ]

        collision = False
        if len(self.projectiles) != nb_projectiles_avant:
            collision = True

        return collision
