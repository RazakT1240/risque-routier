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

# Ponts narratifs : phrase de liaison affichée au-dessus du bouton « suivant »,
# indexée par le chemin de la scène de DESTINATION (le « et maintenant ? »).
PONTS = {
    "/vue-ensemble": "Commençons par l'ampleur : combien de victimes, et où en est la tendance ?",
    "/paradoxe": "Mais ces victimes baissent-elles partout de la même façon ? Pas du tout.",
    "/qui": "On sait où le risque est le plus grave. Reste à savoir qui le subit.",
    "/ou-quand": "Après le « qui », le « où » précis : quels départements, quels moments ?",
    "/evolution": "Ce tableau est-il figé ? Certains usages, eux, explosent.",
    "/simulateur": "Et pour un profil donné, qu'est-ce qui pèse le plus ? À vous d'essayer.",
    "/methode": "D'où viennent tous ces chiffres ? Tout se vérifie.",
}


def voisines(num: int):
    """(précédente, suivante) sous forme (nom, chemin) ou None."""
    prec = SCENES[num - 2] if num > 1 else None
    suiv = SCENES[num] if num < len(SCENES) else None
    return ((prec["nom"], prec["path"]) if prec else None,
            (suiv["nom"], suiv["path"]) if suiv else None)
