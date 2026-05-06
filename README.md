# Space Devastator Solo

Projet d'apprentissage Python avec `pygame-ce`, inspiré de Space Invaders. L'objectif est de
construire une première version limitée, propre et lisible d'un jeu d'arcade 2D. Le joueur doit
survivre à 10 niveaux de difficulté progressive, éliminer les formations ennemies, éviter les
tirs adverses et empêcher l'invasion de la Terre (adversaire qui atteint le niveau du joueur).

## État du projet

Version 1.0.0  - Version finale du projet d'apprentissage

Fonctionnalités présentes :

- boucle principale avec états de jeu
- écran de préparation avec règles, bonus, pénalités et contrôles
- animation d'approche des adversaires au début de chaque niveau
- écrans de victoire et de défaite
- déplacement horizontal du joueur
- tir du joueur avec un seul projectile actif
- formation d'adversaires mobile
- tirs adverses
- adversaire bonus optionnel sur certains niveaux
- collisions joueur, adversaires et projectiles
- pointage, record local sauvegardé dans fichier .cfg, nombre de vies et bonus de victoire
- effets visuels simples
- sons de tir et d'explosion
- vies supplémentaires par tranche de pointage
- affichage plein écran avec surface de rendu logique

## Version 1.0.0

Cette version marque l’achèvement du projet didactique Space Devastator Solo. Cet objectif
a été atteint le 6 mai 2026.

Objectif atteint :
- jeu jouable du début à la fin
- 10 niveaux avec condition de victoire finale
- conditions de défaite
- pointage et record
- sons, sprites et effets visuels simples
- release exécutable Linux et Windows

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
python -m pip install -r requirements.txt
```

Pour préparer une release exécutable, installer aussi les dépendances de
développement :

```bash
python -m pip install -r requirements-dev.txt
```

## Lancement

Depuis le terminal :

```bash
python main.py
```

Par défaut, le jeu démarre en plein écran. Pour lancer en mode fenêtré depuis un terminal :

```bash
MODE_FENETRE=1 python main.py
```

Depuis VSCode :

- ouvrir le dossier du projet ;
- utiliser le profil `Python_PyGame_CE` ;
- lancer avec `F5`.

La configuration de débogage peut utiliser le dossier du projet comme répertoire courant afin 
d'éviter les erreurs de chargement des assets.

## Contrôles

- `Flèche gauche` : déplacer le vaisseau vers la gauche
- `Flèche droite` : déplacer le vaisseau vers la droite
- `A`             : tirer
- `Espace`        : démarrer, continuer ou relancer selon l'état du jeu
- `Échap`         : quitter

## Règles générales

Le joueur doit éliminer toute la formation ennemie pour passer au niveau suivant. La partie 
contient `10` niveaux, avec une difficulté progressive sur la taille des formations, leur vitesse 
et le nombre de canaux de tir ennemis. Les adversaires descendent d'un cran lorsqu'ils touchent un
bord de la zone jouable. Si un adversaire atteint la ligne d'invasion, la partie est perdue.

Une soucoupe bonus jaune peut apparaître une seule fois dans les niveaux pairs. Elle traverse le 
haut de l'écran et rapporte un gros pointage si elle est détruite avant de quitter la zone jouable.
Son apparition est amorcée lorsque la zone haute de la formation ennemie est libre, après un 
certain délai convenu aléatoirement.

## Pointage

Les adversaires rapportent des points selon leur couleur. Un projectile du joueur qui sort de 
l'écran sans toucher d'adversaire enlève `100` points et compte comme tir perdu. Un multiplicateur 
de bonus de fin de niveau est appliqué selon le nombre de tirs perdus. 

Valeurs principales :

- adversaires standards : `100`, `250` ou `500` points selon la ligne ;
- soucoupe bonus : de `1 000` à `5 000` points selon le niveau ;
- projectile perdu : `-100` points.

Une vie supplémentaire est accordée une seule fois pour chaque tranche de `25 000` points atteinte. 
Si le pointage redescend sous une tranche déjà atteinte, puis la franchit de nouveau, aucune 
nouvelle vie bonus n'est donnée pour cette même tranche. Un son dédié est joué pour chaque vie 
bonus obtenue.

Après une victoire de niveau ou une victoire finale, un bonus est ajouté au pointage : vies 
restantes x 250 x multiplicateur de précision

Le multiplicateur dépend du nombre de tirs perdus pendant le niveau :

- `0` tir perdu : bonus `x 5` ;
- `1` à `4` tirs perdus : bonus `x 3` ;
- `5` à `9` tirs perdus : bonus `x 2` ;
- `10` tirs perdus ou plus : bonus `x 1`.

Le total est affiché avec une animation de comptage à cadence constante. Le pointage monte par 
tranches de points avec un son montant, et le joueur peut appuyer sur `Espace` pour terminer  'animation immédiatement.

## Niveaux

Les paramètres des niveaux sont regroupés dans `niveaux.py`. Chaque niveau définit :

- le nombre de colonnes et de lignes d'adversaires
- la vitesse de déplacement de la formation
- le nombre de canaux de tir adverses
- l'espacement entre chacun des adversaires
- l'activation, la vitesse et la valeur de la soucoupe bonus.

La progression actuelle va de petites formations de `6 x 2` adversaires à une formation finale de 
`10 x 4` adversaires, avec jusqu'à `5` canaux de tir adverses.

## Structure

```text
.
├── assets/
│   ├── images/
│   └── sons/
├── commun.py
├── config.py
├── chemins.py
├── effets.py
├── etats.py
├── main.py
├── objets.py
├── niveaux.py
├── requirements-dev.txt
├── requirements.txt
├── space_devastator_solo.spec
└── README.md
```

Rôle des principaux fichiers :

- `main.py` : boucle principale, états du jeu, événements et rendu
- `config.py` : paramètres stables du jeu
- `chemins.py` : chemins des assets et du fichier de configuration utilisateur
- `niveaux.py` : progression et paramètres propres à chaque niveau
- `etats.py` : énumérations des états et directions
- `objets.py` : joueur, adversaires, projectiles et formation
- `effets.py` : effets visuels temporaires
- `commun.py` : minuteurs, clignotement et affichage de texte
- `requirements.txt` : dépendances Python du projet
- `requirements-dev.txt` : dépendances nécessaires pour construire une release
- `space_devastator_solo.spec` : configuration PyInstaller suivie par Git

## Release PyInstaller

La release recommandée utilise PyInstaller en mode `onedir`. Ce mode produit un dossier complet contenant l'exécutable et ses fichiers internes, ce qui est plus fiable pour un jeu `pygame-ce` 
avec images et sons.

Construire la release depuis l'environnement virtuel :

```bash
python -m PyInstaller --clean --noconfirm space_devastator_solo.spec
```

Le résultat attendu est un dossier :

```text
dist/
└── space_devastator_solo/
    ├── space_devastator_solo
    └── _internal/
```

Sous Windows, l'exécutable porte l'extension `.exe`. Les assets du dossier
`assets/` sont embarqués dans la release par le fichier `.spec`. Il faut
construire la release Windows depuis Windows et la release Linux depuis Linux.

## Notes techniques

Le jeu utilise une surface logique de `1280 x 800` pixels. En mode fenêtré, la
fenêtre reprend directement cette taille. En plein écran, la surface logique est
centrée et redimensionnée seulement si nécessaire, avec des bandes noires autour
si le ratio de l'écran ne correspond pas.

Ce choix remplace l'utilisation directe de `pygame.SCALED`, qui dégradait le
rendu du texte et de l'image sur la configuration de développement utilisée.

Le fond principal est chargé depuis `assets/images/fond_ecran.png`, puis adapté
à la résolution logique du jeu. Les chemins d'assets sont résolus depuis le
dossier du projet en développement et depuis le bundle PyInstaller en release.

Le record est sauvegardé dans `sds.cfg`, hors du dossier du jeu :

- Windows : `%APPDATA%\Space Devastator Solo\sds.cfg` ;
- Linux : `$XDG_CONFIG_HOME/space-devastator-solo/sds.cfg`, ou
  `~/.config/space-devastator-solo/sds.cfg` si `XDG_CONFIG_HOME` n'est pas
  défini.

Au premier lancement après migration, si un ancien `sds.cfg` existe encore à la
racine du projet et qu'aucun fichier utilisateur n'existe, le record est relu
puis sauvegardé au nouvel emplacement.

## Licence

Projet personnel d'apprentissage. Aucune licence publique n'est définie pour le moment.
