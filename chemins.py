"""Gestion des chemins du jeu en développement et en release."""

import os
import sys

from pathlib import Path


NOM_FICHIER_CONFIG = "sds.cfg"
NOM_DOSSIER_CONFIG_WINDOWS = "Space Devastator Solo"
NOM_DOSSIER_CONFIG_LINUX = "space-devastator-solo"


def chemin_ressource(chemin_relatif: str) -> Path:
    """
    Retourne le chemin absolu d'une ressource du jeu.

    En développement, les ressources sont lues depuis le dossier du projet.
    En release PyInstaller, elles sont lues depuis le dossier temporaire ou interne du bundle.
    """

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        racine = Path(sys._MEIPASS)
    else:
        racine = Path(__file__).resolve().parent

    return racine / chemin_relatif


def chemin_config_utilisateur() -> Path:
    """
    Retourne l'emplacement du fichier de configuration utilisateur.
    """

    if os.name == "nt":
        dossier_base = os.environ.get("APPDATA")

        if dossier_base is None:
            dossier_base = Path.home() / "AppData" / "Roaming"
        else:
            dossier_base = Path(dossier_base)

        return dossier_base / NOM_DOSSIER_CONFIG_WINDOWS / NOM_FICHIER_CONFIG

    dossier_base = os.environ.get("XDG_CONFIG_HOME")

    if dossier_base is None:
        dossier_base = Path.home() / ".config"
    else:
        dossier_base = Path(dossier_base)

    return dossier_base / NOM_DOSSIER_CONFIG_LINUX / NOM_FICHIER_CONFIG


def chemin_ancien_config_projet() -> Path:
    """
    Retourne l'ancien emplacement du fichier de configuration dans le projet.
    """

    return Path(__file__).resolve().parent / NOM_FICHIER_CONFIG
