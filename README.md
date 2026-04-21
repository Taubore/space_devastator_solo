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
- En fenêtré, la fenêtre utilise directement cette taille
- En plein écran, l'image du jeu reste centrée sans étirement ; des bords noirs
  sont affichés autour si la résolution réelle est plus grande
- Ce contournement remplace `pygame.SCALED`, qui dégradait le rendu du texte et
  de l'image sur cette configuration
