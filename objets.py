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
        self.minuteur = Minuteur(500)
        
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
        Dessine le projectile sous forme de rectangle et si le projectile est entrain de 
        sortir de l'écran on affiche le retrait de pointage
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

    def occupe_zone(self, rect: pygame.Rect) -> bool:
        """
        Indique si au moins un adversaire occupe le rectangle donné.
        """

        return any(adv.rect.colliderect(rect) for adv in self.adversaires)

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


class AdversaireBonus:
    """
    Adversaire bonus traversant le haut de l'écran.
    """

    def __init__(
        self,
        direction: DirectionHorizontale,
        vitesse: int,
        config: Configuration,
    ) -> None:
        """
        Constructeur.
        """

        self.config = config
        self.direction = direction
        self.vitesse = vitesse
        self.rect = pygame.Rect(
            0,
            config.limite_y_min_zone_jouable,
            config.largeur_adversaire,
            config.hauteur_adversaire,
        )

        if direction is DirectionHorizontale.DROITE:
            self.rect.left = config.limite_x_min_zone_jouable
        else:
            self.rect.right = config.limite_x_max_zone_jouable

        self.image = pygame.image.load(config.image_adversaire_bonus).convert_alpha()
        self.image = pygame.transform.smoothscale(
            self.image,
            (config.largeur_adversaire, config.hauteur_adversaire),
        )

    @property
    def est_sorti(self) -> bool:
        """
        Indique si l'adversaire bonus a quitté la zone jouable.
        """

        if self.direction is DirectionHorizontale.DROITE:
            return self.rect.left > self.config.limite_x_max_zone_jouable

        return self.rect.right < self.config.limite_x_min_zone_jouable

    def mettre_a_jour(self) -> None:
        """
        Déplace l'adversaire bonus horizontalement.
        """

        self.rect.x += int(self.direction) * self.vitesse

    def dessiner(self, surface: pygame.Surface) -> None:
        """
        Dessine l'adversaire bonus.
        """

        surface.blit(self.image, self.rect)

    def verifier_collision(self, rect: pygame.Rect) -> bool:
        """
        Vérfie s'il y a collision avec le rectangle passé en paramètre.
        """
        
        rect_reduit = self.rect.inflate(0, -30)

        return rect_reduit.colliderect(rect)


class GestionAdversaireBonus:
    """
    Contrôle l'apparition unique de l'adversaire bonus pour un niveau.
    """

    def __init__(self, son: pygame.mixer.Sound, config: Configuration) -> None:
        """
        Constructeur.
        """

        self.son = son
        self.config = config
        self.adversaire: AdversaireBonus | None = None
        self.minuteur_apparition: Minuteur | None = None
        self.actif = False
        self.est_apparu = False
        self.vitesse = 0
        self.delai_min_ms = 0
        self.delai_max_ms = 0

    def initialiser(
        self,
        actif: bool,
        vitesse: int,
        delai_min_ms: int,
        delai_max_ms: int,
    ) -> None:
        """
        Réinitialise l'adversaire bonus pour le niveau courant.
        """

        self.actif = actif
        self.vitesse = vitesse
        self.delai_min_ms = delai_min_ms
        self.delai_max_ms = max(delai_min_ms, delai_max_ms)
        self.adversaire = None
        self.minuteur_apparition = None
        self.est_apparu = False

    def mettre_a_jour(self, formation: FormationAdversaires) -> None:
        """
        Amorce l'apparition et met à jour l'adversaire bonus actif.
        """

        if self.adversaire is not None:
            self.adversaire.mettre_a_jour()

            if self.adversaire.est_sorti:
                self.retirer_adversaire()

            return

        if not self.actif or self.est_apparu:
            return

        if self.minuteur_apparition is None:
            if not formation.occupe_zone(self._rect_declenchement()):
                delai_ms = random.randint(self.delai_min_ms, self.delai_max_ms)
                self.minuteur_apparition = Minuteur(delai_ms)
                self.minuteur_apparition.demarrer()
            return

        if self.minuteur_apparition.est_termine:
            self._faire_apparaitre()

    def dessiner(self, surface: pygame.Surface) -> None:
        """
        Dessine l'adversaire bonus s'il est présent.
        """

        if self.adversaire is not None:
            self.adversaire.dessiner(surface)

    def _rect_declenchement(self) -> pygame.Rect:
        """
        Retourne la zone haute qui doit être libre pour amorcer le minuteur.
        """

        return pygame.Rect(
            self.config.limite_x_min_zone_jouable,
            self.config.limite_y_min_zone_jouable,
            self.config.limite_x_max_zone_jouable
            - self.config.limite_x_min_zone_jouable,
            self.config.hauteur_zone_declenchement_adversaire_bonus,
        )

    def _faire_apparaitre(self) -> None:
        """
        Crée l'adversaire bonus et joue son son d'apparition.
        """

        direction = random.choice(
            [DirectionHorizontale.GAUCHE, DirectionHorizontale.DROITE]
        )
        self.adversaire = AdversaireBonus(direction, self.vitesse, self.config)
        self.est_apparu = True
        self.son.play(loops=-1)

    def retirer_adversaire(self) -> None:
        """
        Retire l'adversaire bonus et arrête son son s'il est visible.
        """

        self.son.stop()
        self.adversaire = None    


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

    VITESSE_TIR_INITIAL_MIN = 2000
    VITESSE_TIR_INITIAL_MAX = 6000

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
            self.minuteurs[index_minuteur].demarrer()

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
                if self.minuteurs[index_tir].est_termine:
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
