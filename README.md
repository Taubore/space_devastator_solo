# Space Devastator Solo

Projet d'apprentissage Python avec `pygame-ce`, inspiré de Space Invaders.
L'objectif est de construire une première version limitée, propre et lisible
d'un jeu d'arcade 2D.

## État du projet

Version en cours de développement.

Fonctionnalités présentes :

- boucle principale avec états de jeu ;
- écran de préparation, victoire et défaite ;
- déplacement horizontal du joueur ;
- tir du joueur avec un seul projectile actif ;
- formation d'adversaires mobile ;
- tirs adverses ;
- adversaire bonus optionnel par niveau ;
- collisions joueur, adversaires et projectiles ;
- pointage, nombre de vies et bonus de victoire ;
- effets visuels simples ;
- sons de tir et d'explosion ;
- affichage plein écran avec surface de rendu logique.

## Prérequis

- Python `3.12`
- environnement virtuel `.venv`
- `pygame-ce`

## Installation

Créer et activer l'environnement virtuel :

```bash
python -m venv .venv
source .venv/bin/activate
```

Installer la dépendance principale :

```bash
python -m pip install pygame-ce
```

## Lancement

Depuis le terminal :

```bash
python main.py
```

Depuis VSCode :

- ouvrir le dossier du projet ;
- utiliser le profil `Python_PyGame_CE` ;
- lancer avec `F5`.

La configuration de débogage peut utiliser le dossier du projet comme
répertoire courant afin d'éviter les erreurs de chargement des assets.

## Contrôles

- `Flèche gauche` : déplacer le vaisseau vers la gauche
- `Flèche droite` : déplacer le vaisseau vers la droite
- `A` : tirer
- `Espace` : démarrer, continuer ou relancer selon l'état du jeu
- `Échap` : quitter

## Pointage

Les adversaires rapportent des points selon leur type. Un projectile du joueur
qui sort de l'écran sans toucher d'adversaire retire `100` points si le pointage
est positif.

Après une victoire de niveau ou une victoire finale, un bonus est ajouté au
pointage :

```text
vies restantes x 250 x niveau terminé
```

Le total est affiché avec une animation de comptage à cadence constante. Le
pointage monte par tranches de points avec un son montant, et la durée totale
s'adapte au bonus obtenu.

## Niveaux

Les paramètres des niveaux sont regroupés dans `niveaux.py`. Chaque niveau peut
activer ou désactiver l'adversaire bonus avec `adversaire_bonus_actif`, puis
régler sa vitesse et son délai d'apparition aléatoire.

L'adversaire bonus apparaît au maximum une fois par niveau. Son minuteur est
amorcé lorsque la zone haute jouable est libre d'adversaires.

## Structure

```text
.
├── assets/
│   ├── images/
│   └── sons/
├── commun.py
├── config.py
├── effets.py
├── etats.py
├── main.py
├── objets.py
└── README.md
```

Rôle des principaux fichiers :

- `main.py` : boucle principale, états du jeu, événements et rendu ;
- `config.py` : paramètres stables du jeu ;
- `niveaux.py` : progression et paramètres propres à chaque niveau ;
- `etats.py` : énumérations des états et directions ;
- `objets.py` : joueur, adversaires, projectiles et formation ;
- `effets.py` : effets visuels temporaires ;
- `commun.py` : utilitaires partagés.

## Notes techniques

Le jeu utilise une surface logique de `1280 x 800` pixels. En mode fenêtré, la
fenêtre reprend directement cette taille. En plein écran, la surface logique est
centrée et redimensionnée seulement si nécessaire, avec des bandes noires autour
si le ratio de l'écran ne correspond pas.

Ce choix remplace l'utilisation directe de `pygame.SCALED`, qui dégradait le
rendu du texte et de l'image sur la configuration de développement utilisée.

Le fond principal est chargé depuis `assets/images/fond_ecran.png`, puis adapté
à la résolution logique du jeu. Les chemins d'assets sont relatifs au dossier du
projet.

## Licence

Projet personnel d'apprentissage. Aucune licence publique n'est définie pour le
moment.
