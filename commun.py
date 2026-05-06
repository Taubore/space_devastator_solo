import pygame


class Minuteur:
    """
    Mesure une durée après un démarrage explicite.
    """

    def __init__(self, duree_ms: int) -> None:
        self.duree_ms = duree_ms
        self.instant_depart = 0
        self.actif = False

    @property
    def est_actif(self) -> bool:
        return self.actif

    @property
    def est_termine(self) -> bool:
        if not self.actif:
            return False

        temps_ecoule = pygame.time.get_ticks() - self.instant_depart
        return temps_ecoule >= self.duree_ms

    def demarrer(self) -> None:
        self.instant_depart = pygame.time.get_ticks()
        self.actif = True

    def arreter(self) -> None:
        self.actif = False

    def reinitialiser(self) -> None:
        self.demarrer()

    def modifier_duree(self, duree_ms: int) -> None:
        self.duree_ms = duree_ms

class Clignotement:
    """
    Gère un affichage visible / caché selon une demi-période en ms.
    """

    def __init__(self, duree_ms: int = 500, visible_au_depart: bool = True) -> None:
        """
        Constructeur
        """

        self.visible_au_depart = visible_au_depart
        self.minuteur_phase = Minuteur(duree_ms)

    @property
    def duree_ms(self) -> int:
        """
        Retourne la durée d'une phase visible ou cachée.
        """

        return self.minuteur_phase.duree_ms

    def changer_duree(self, duree_ms: int) -> None:
        """
        Met à jour la durée d'une phase de clignotement.
        """

        self.minuteur_phase.modifier_duree(duree_ms)

    def est_visible(self, instant_ms: int) -> bool:
        """
        Indique si l'élément doit être affiché à cet instant.
        """

        if self.duree_ms <= 0:
            return True

        phase_visible = (
            ((instant_ms - self.minuteur_phase.instant_depart) // self.duree_ms) % 2
            == 0
        )
        return phase_visible if self.visible_au_depart else not phase_visible

    def reinitialiser(self) -> None:
        """
        Relance le clignotement depuis une phase visible ou cachée initiale.
        """

        self.minuteur_phase.reinitialiser()


class AfficheurTexte:
    RATIO_ESPACEMENT_LIGNES = 0.35

    def __init__(
        self,
        surface: pygame.Surface,
        taille_defaut: int,
        couleur_defaut: tuple[int, int, int],
        police: str = "",
    ) -> None:
        """
        Constructeur
        """

        self.surface = surface
        self.taille = taille_defaut
        self.couleur = couleur_defaut
        self.police = pygame.font.Font(None if police == "" else police, taille_defaut)

    def dessiner(
        self,
        texte: str,
        pct_x: int,
        pct_y: int | pygame.Rect | None = None,
        taille: int = -1,
        couleur: tuple[int, int, int] = (-1, -1, -1),
        rect_precedent: pygame.Rect | None = None,
    ) -> pygame.Rect:
        """
        Dessine le texte avec un X en pourcentage et un Y absolu ou relatif.

        Le Y absolu est calculé avec pct_y, en pourcentage de la surface.
        Le Y relatif est calculé à partir du rect de la ligne précédente.
        """
        if isinstance(pct_y, pygame.Rect):
            if rect_precedent is not None:
                raise ValueError(
                    "Utilisez pct_y ou rect_precedent, mais pas les deux."
                )
            rect_precedent = pct_y
            pct_y = None

        if rect_precedent is not None and pct_y is not None:
            raise ValueError("Utilisez pct_y ou rect_precedent, mais pas les deux.")

        if rect_precedent is None and pct_y is None:
            raise ValueError("pct_y ou rect_precedent doit être fourni.")

        if taille != -1:
            self.police.point_size = taille
        else:
            self.police.point_size = self.taille

        couleur_texte = couleur if couleur != (-1, -1, -1) else self.couleur

        surface_txt = self.police.render(
            texte,
            True,
            couleur_texte,
        )

        position_x = round(self.surface.get_width() * pct_x / 100)
        decalage_x = round(surface_txt.get_width() * pct_x / 100)

        if rect_precedent is None:
            assert isinstance(pct_y, int)
            position_y = round(self.surface.get_height() * pct_y / 100)
            decalage_y = round(surface_txt.get_height() * pct_y / 100)
        else:
            espacement_y = round(
                rect_precedent.height * self.RATIO_ESPACEMENT_LIGNES
            )
            position_y = rect_precedent.bottom + espacement_y
            decalage_y = 0

        rect = surface_txt.get_rect(
            topleft=(position_x - decalage_x, position_y - decalage_y)
        )
        
        self.surface.blit(surface_txt, rect)

        return rect
        
