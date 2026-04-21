"""Programme principal du jeu Space Devastator Solo"""

import sys
import pygame

from config import Configuration
from etats import EtatJeu
from objets import Joueur, Adversaire

class Jeu:
    """Classe principale du jeu."""

    def __init__(self) -> None:
        """Initialisation de l'objet de la classe."""

        pygame.init()

        self.config = Configuration()
        self.fenetre = pygame.display.set_mode(
            (self.config.largeur_fenetre, self.config.hauteur_fenetre),
            pygame.FULLSCREEN | pygame.SCALED,
        )
        self.horloge = pygame.time.Clock()
        self.etat = EtatJeu.PREPARATION

        self.joueur = Joueur(self.config)
        self.adversaires = self._creer_grille_adversaires()

        self.police_base = pygame.font.Font(None, self.config.taille_police_base)

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
        pass

    def _dessiner(self) -> None:
        """Dessine la scène complète."""

        self.fenetre.fill(self.config.couleur_fond)

        for adv in self.adversaires:
            adv.dessiner(self.fenetre, self.config)

        self.joueur.dessiner(self.fenetre, self.config)
        self._dessiner_etat()

        pygame.display.flip()

    def _dessiner_etat(self) -> None:
        """Affiche un court texte de diagnostic de l'état courant."""

        texte = f"État : {self.etat.name} | Aliens : {len(self.adversaires)}"
        image_texte = self.police_base.render(
            texte,
            True,
            self.config.couleur_texte,
        )
        self.fenetre.blit(image_texte, (20, 20))

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