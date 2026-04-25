import pygame


class Minuteur:
    """
    Gère une durée mesurée à partir de l'instant de construction ou de
    réinitialisation.
    """

    def __init__(self, duree_ms: int, demarrer: bool = True) -> None:
        """
        Construit un minuteur générique basé sur l'horloge de pygame.
        """

        self.duree_ms = duree_ms
        self.instant_depart = 0

        if demarrer:
            self.reinitialiser()

    def est_termine(self, instant_ms: int | None = None) -> bool:
        """
        Retourne True lorsque la durée configurée est atteinte.
        """

        if self.duree_ms <= 0:
            return True

        if instant_ms is None:
            instant_ms = pygame.time.get_ticks()

        return instant_ms - self.instant_depart >= self.duree_ms

    def reinitialiser(self) -> None:
        """
        Relance le minuteur à partir de l'instant courant.
        """

        self.instant_depart = pygame.time.get_ticks()

    def changer_duree(self, duree_ms: int, reinitialiser: bool = False) -> None:
        """
        Met à jour la durée. Réinitialise aussi le départ si demandé.
        """

        self.duree_ms = duree_ms

        if reinitialiser:
            self.reinitialiser()


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

    def changer_duree(self, duree_ms: int, reinitialiser: bool = False) -> None:
        """
        Met à jour la durée d'une phase de clignotement.
        """

        self.minuteur_phase.changer_duree(duree_ms, reinitialiser)

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
