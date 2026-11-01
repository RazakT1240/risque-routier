"""Registre des 8 scènes : numéro, nom, chemin, icône (navigation, progression)."""

SCENES = [
    {"num": 1, "nom": "Accueil", "path": "/", "icon": "tabler:road"},
    {"num": 2, "nom": "Vue d'ensemble", "path": "/vue-ensemble", "icon": "tabler:chart-line"},
    {"num": 3, "nom": "Le paradoxe", "path": "/paradoxe", "icon": "tabler:arrows-diff"},
    {"num": 4, "nom": "Qui", "path": "/qui", "icon": "tabler:users"},
    {"num": 5, "nom": "Où et quand", "path": "/ou-quand", "icon": "tabler:map-pin"},
    {"num": 6, "nom": "Ce qui change", "path": "/evolution", "icon": "tabler:trending-up"},
    {"num": 7, "nom": "Simulateur", "path": "/simulateur", "icon": "tabler:adjustments"},
    {"num": 8, "nom": "Méthode et données", "path": "/methode", "icon": "tabler:database"},
]
PAR_CHEMIN = {s["path"]: s for s in SCENES}


def voisines(num: int):
    """(précédente, suivante) sous forme (nom, chemin) ou None."""
    prec = SCENES[num - 2] if num > 1 else None
    suiv = SCENES[num] if num < len(SCENES) else None
    return ((prec["nom"], prec["path"]) if prec else None,
            (suiv["nom"], suiv["path"]) if suiv else None)
