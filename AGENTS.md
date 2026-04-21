# AGENTS.md

## Projet
`space_devastator_solo` projet d’apprentissage de Python avec `pygame-ce`. 

## Contexte d'apprentissage
- Je viens de terminer un premier projet pong_devastator_solo. 
- Ce projet Pong m’a permis de consolider : 
  - la boucle principale d’un jeu avec pygame-ce;
  - les événements clavier;
  - les états de jeu avec Enum;
  - les classes simples comme Jeu, Balle, Raquette;
  - les collisions avec pygame.Rect;
  - les sons et sprites;
  - une IA simple;
  - une physique de balle avec direction normalisée;
  - une configuration extraite dans une classe dédiée;
  - un écran titre, une mise au jeu, un écran de fin et une boucle complète.
  - J’ai une bonne expérience passée en programmation objet avec C++ et C#, donc il ne faut pas m’expliquer trop lentement les bases de l’objet.
  - Je veux progresser plus rapidement que dans un tutoriel débutant complet, mais sans brûler les étapes importantes propres au développement de jeux 2D
  - Je veux m'assurer de respecter les bonnes pratiques en matière de développement de jeux, mais sans en faire une règle trop stricte.

## Environnement
- Linux
- VSCode
- Profil VSCode : `Python_PyGame_CE`
- Environnement Python : `.venv`
- Python : `3.12.3`
- Bibliothèque : `pygame-ce`
- Projet personnel sur GitHub

## Règles
- Privilégier un code lisible, maintenable, pédagogique, mais pas trop lent ni trop scolaire.
- Avancer par étapes concrètes, mais pas trop petites.
- Éviter la surconception.
- Ne pas créer de nouveaux fichiers ou dossiers sans besoin réel.
- Faire des changements petits, lisibles et faciles à tester.
- Ne pas utiliser les chaînes littérales pour les conditions, utiliser constantes, enum, dataclasses, etc. en respectant les bonnes pratiques
- Garder Git/GitHub propre : branches simples, commits fréquents, messages de commit en français.
- Maintenir un fichier README.md à jour en respectant les bonnes pratiques de développement communautaire (GitHub).

## Style
- Commentaires en français.
- Noms Python en français sans accents.
- Commentaires, docstrings et textes utilisateur en français normal avec accents.
- Conserver en anglais les éléments imposés par Python et Pygame.
- Limiter les lignes à 88 caractères. 
- Code bien aéré et suffisament documenté en respectant les bonne pratiques de développement communautaire (GitHub).

## Objectif actuel
Créer une version 1 limitée et propre d’un Space Invaders simplifié.