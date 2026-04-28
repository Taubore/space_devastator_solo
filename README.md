# space_devastator_solo

Projet d'apprentissage Python avec `pygame-ce` pour construire une version
simple et propre d'un Space Invaders.

## Prérequis

- Python `3.12`
- Environnement virtuel `.venv`
- `pygame-ce`

## Lancement

Depuis le terminal :

```bash
python main.py
```

Depuis VSCode :

- `F5` lance directement `main.py`
- La configuration de débogage utilise le dossier du projet comme répertoire
  courant pour éviter les erreurs liées au fichier actif

## Affichage

- Le jeu conserve une zone de rendu logique en `1280 x 800` (16:10)
- Le fond principal est chargé depuis `assets/images/fond_ecran.png`, puis
  redimensionné une seule fois vers la résolution logique du jeu
- En fenêtré, la fenêtre utilise directement cette taille
- En plein écran, l'image du jeu reste centrée sans étirement ; des bords noirs
  sont affichés autour si la résolution réelle est plus grande
- Ce contournement remplace `pygame.SCALED`, qui dégradait le rendu du texte et
  de l'image sur cette configuration
- Les délais simples du jeu peuvent utiliser l'utilitaire `Minuteur`
  basé sur `pygame.time.get_ticks()`
- `Clignotement` reste disponible comme surcouche spécialisée pour les
  affichages visibles / cachés
- La durée par défaut `duree_clignotement_defaut_ms = 500` correspond à
  `500 ms` visible puis `500 ms` masqué
- Au lancement d'un tableau, les adversaires ont une courte animation
  d'approche : ils apparaissent un à un, grossissent jusqu'à leur taille
  normale, puis restent visibles avant le début réel de la partie
- La vitesse de cette approche est réglée par
  `duree_approche_adversaire_ms` dans `config.py`
- Les adversaires arrivent un à un dans un ordre aléatoire ; chaque adversaire
  passe de petit à sa taille normale avant que le suivant commence
