import pygame

class Clignotement:
    """
    Gère un affichage visible / caché selon une demi-période en ms.
    """

    def __init__(self, duree_ms: int = 500, visible_au_depart: bool = True) -> None:
        """
        Constructeur
        """

        self.duree_ms = duree_ms
        self.visible_au_depart = visible_au_depart
        self.instant_depart = pygame.time.get_ticks()

    def est_visible(self, instant_ms: int) -> bool:
        """
        Indique si l'élément doit être affiché à cet instant.
        """

        if self.duree_ms <= 0:
            return True

        phase_visible = ((instant_ms - self.instant_depart) // self.duree_ms) % 2 == 0
        return phase_visible if self.visible_au_depart else not phase_visible

    def reinitialiser(self) -> None:
        """
        Relance le clignotement depuis une phase visible ou cachée initiale.
        """

        self.instant_depart = pygame.time.get_ticks()
