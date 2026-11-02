"""Internationalisation : cadre applicatif bilingue (français par défaut, anglais en option).

La langue est portée par un cookie `langue` (fr/en). Comme `app.layout` et les `layout()`
des pages sont des fonctions appelées à chaque requête, `t()` lit le cookie via Flask et
renvoie le bon texte sans rechargement de module.

Périmètre traduit : tout le CADRE (en-tête, navigation, filtres, assistant, boutons) et le
SIMULATEUR. Les titres-messages analytiques des scènes 02–06 sont générés depuis les données
(G3) et restent en français dans ce lot : leur version anglaise doit être validée par le
propriétaire (un titre doit refléter les données, jamais mentir).
"""

from __future__ import annotations

import flask

LANGUES = ("fr", "en")


def langue() -> str:
    """Langue courante depuis le cookie (fr par défaut, hors contexte de requête aussi)."""
    try:
        if flask.has_request_context():
            lg = flask.request.cookies.get("langue", "fr")
            return lg if lg in LANGUES else "fr"
    except Exception:
        pass
    return "fr"


def t(cle: str, defaut: str | None = None) -> str:
    """Texte traduit pour la clé donnée, dans la langue courante."""
    d = TR.get(cle)
    if d is None:
        return defaut if defaut is not None else cle
    lg = langue()
    return d.get(lg) or d.get("fr") or cle


def nom_scene(path: str) -> str:
    d = NOMS.get(path)
    return (d.get(langue()) or d.get("fr")) if d else path


def pont(path: str) -> str | None:
    d = PONTS.get(path)
    return (d.get(langue()) or d.get("fr")) if d else None


def opt(categorie: str, valeurs: list[str]) -> list[dict]:
    """Options d'un contrôle : la VALEUR reste la clé de données (français, lue par le modèle),
    seul le LIBELLÉ affiché est traduit."""
    table = VALEURS.get(categorie, {})
    lg = langue()
    return [{"value": v, "label": (table.get(v, {}).get(lg) or v)} for v in valeurs]


# Libellés d'affichage des valeurs de données du simulateur (la valeur reste en français)
VALEURS = {
    "type_usager": {
        "Piéton": {"en": "Pedestrian"}, "Vélo": {"en": "Bicycle"}, "EDP": {"en": "E-scooter"},
        "2RM": {"en": "Motorcycle"}, "Voiture": {"en": "Car"}, "Utilitaire": {"en": "Van"},
        "Poids lourd": {"en": "Truck"}, "Bus, car, tram": {"en": "Bus / coach / tram"},
        "Autre": {"en": "Other"}},
    "sexe": {"Homme": {"en": "Male"}, "Femme": {"en": "Female"}},
    "route": {
        "Autoroute": {"en": "Motorway"}, "Nationale": {"en": "Trunk road"},
        "Départementale": {"en": "Departmental"}, "Communale": {"en": "Local"},
        "Métropole urbaine": {"en": "Urban metropolis"}, "Autre": {"en": "Other"}},
}


# --- Noms courts des scènes (navbar, compteur, boutons de navigation) -------
NOMS = {
    "/": {"fr": "Accueil", "en": "Home"},
    "/vue-ensemble": {"fr": "Vue d'ensemble", "en": "Overview"},
    "/paradoxe": {"fr": "Le paradoxe", "en": "The paradox"},
    "/qui": {"fr": "Qui", "en": "Who"},
    "/ou-quand": {"fr": "Où et quand", "en": "Where & when"},
    "/evolution": {"fr": "Ce qui change", "en": "What's changing"},
    "/simulateur": {"fr": "Simulateur", "en": "Simulator"},
    "/methode": {"fr": "Méthode et données", "en": "Method & data"},
}

# --- Ponts narratifs (phrase de liaison, indexée par chemin de destination) --
PONTS = {
    "/vue-ensemble": {
        "fr": "Commençons par l'ampleur : combien de victimes, et où en est la tendance ?",
        "en": "Let's start with the scale: how many casualties, and which way is the trend going?"},
    "/paradoxe": {
        "fr": "Mais ces victimes baissent-elles partout de la même façon ? Pas du tout.",
        "en": "But are casualties falling the same way everywhere? Not at all."},
    "/qui": {
        "fr": "On sait où le risque est le plus grave. Reste à savoir qui le subit.",
        "en": "We know where risk is most severe. Now, who bears it?"},
    "/ou-quand": {
        "fr": "Après le « qui », le « où » précis : quels départements, quels moments ?",
        "en": "After the \"who\", the precise \"where\": which areas, which moments?"},
    "/evolution": {
        "fr": "Ce tableau est-il figé ? Certains usages, eux, explosent.",
        "en": "Is this picture static? Some modes, in fact, are soaring."},
    "/simulateur": {
        "fr": "Et pour un profil donné, qu'est-ce qui pèse le plus ? À vous d'essayer.",
        "en": "And for a given profile, what weighs most? Try it yourself."},
    "/methode": {
        "fr": "D'où viennent tous ces chiffres ? Tout se vérifie.",
        "en": "Where do all these figures come from? Everything is verifiable."},
}

# --- Textes du cadre (clés dotées) ------------------------------------------
TR = {
    # En-tête / marque
    "brand.sub": {"fr": "Fréquence · Gravité · Coût", "en": "Frequency · Severity · Cost"},
    "header.menu": {"fr": "Ouvrir la navigation", "en": "Open navigation"},
    "header.theme": {"fr": "Basculer le thème clair / sombre", "en": "Toggle light / dark theme"},
    "header.logout": {"fr": "Se déconnecter", "en": "Sign out"},
    "header.langue": {"fr": "Langue de l'interface", "en": "Interface language"},
    "header.compteur": {"fr": "Scène", "en": "Scene"},
    # Navbar
    "nav.badge": {"fr": "Challenge Dataviz · Institut des Actuaires",
                  "en": "Dataviz Challenge · Institut des Actuaires"},
    "nav.replier": {"fr": "Replier le menu", "en": "Collapse menu"},
    "nav.replier_aria": {"fr": "Replier ou déplier le menu", "en": "Collapse or expand menu"},
    "nav.scene_aria": {"fr": "Scène", "en": "Scene"},
    # Filtres
    "filtres.ouvrir": {"fr": "Ouvrir les filtres", "en": "Open filters"},
    "filtres.periode": {"fr": "Période", "en": "Period"},
    "filtres.territoire": {"fr": "Territoire", "en": "Area"},
    "filtres.france": {"fr": "France métropolitaine", "en": "Metropolitan France"},
    "filtres.chercher_dep": {"fr": "Rechercher un département…", "en": "Search a department…"},
    "filtres.aucun_dep": {"fr": "Aucun département", "en": "No department"},
    "filtres.note_annees": {"fr": "Les courbes d'évolution montrent toujours les 7 années.",
                            "en": "Trend charts always show all 7 years."},
    "filtres.pire": {"fr": "Département le plus touché", "en": "Hardest-hit department"},
    "filtres.reset": {"fr": "Réinitialiser", "en": "Reset"},
    "filtres.pied": {"fr": "Les filtres s'appliquent à toutes les scènes et à l'adresse de "
                           "la page.",
                     "en": "Filters apply to every scene and to the page URL."},
    # Encart « Et alors ? » et navigation
    "insight.label": {"fr": "Et alors ?", "en": "So what?"},
    "nav.precedente": {"fr": "Scène précédente", "en": "Previous scene"},
    "nav.suivante": {"fr": "Scène suivante", "en": "Next scene"},
    "nav.aria": {"fr": "Navigation entre scènes", "en": "Scene navigation"},
    # Assistant
    "assist.ouvrir": {"fr": "Poser une question", "en": "Ask a question"},
    "assist.ouvrir_aria": {"fr": "Ouvrir l'assistant de questions sur les données",
                           "en": "Open the data question assistant"},
    "assist.titre": {"fr": "Assistant · vos questions sur les données",
                     "en": "Assistant · your questions on the data"},
    "assist.intro": {
        "fr": "Posez une question sur les chiffres du tableau de bord. Les réponses sont "
              "calculées depuis les données (aucun chiffre n'est inventé).",
        "en": "Ask a question about the dashboard figures. Answers are computed from the data "
              "(no figure is invented). The assistant understands French keywords."},
    "assist.placeholder": {"fr": "Ex. : combien de tués en 2025 ?",
                           "en": "e.g. combien de tués en 2025 ?"},
    "assist.q_aria": {"fr": "Votre question", "en": "Your question"},
    "assist.chercher": {"fr": "Chercher la réponse", "en": "Find the answer"},
    "assist.exemples": {"fr": "Exemples", "en": "Examples"},
    "assist.source": {"fr": "Source", "en": "Source"},
    "assist.voir": {"fr": "Voir", "en": "See"},
    "assist.vide": {
        "fr": "Aucune réponse trouvée dans les données pour cette question. Essayez un des "
              "exemples, ou reformulez avec un mot-clé (tués, accidents, département, "
              "deux-roues, pluie…).",
        "en": "No answer found in the data for this question. Try one of the examples, or "
              "rephrase with a French keyword (tués, accidents, département, deux-roues, "
              "pluie…)."},
    "assist.compteur_une": {"fr": "réponse trouvée dans les données",
                            "en": "answer found in the data"},
    "assist.compteur_plus": {"fr": "réponses trouvées dans les données",
                             "en": "answers found in the data"},
    # Simulateur
    "sim.profil": {"fr": "Le profil", "en": "The profile"},
    "sim.type": {"fr": "Type d'usager", "en": "Road user type"},
    "sim.age": {"fr": "Âge", "en": "Age"},
    "sim.sexe": {"fr": "Sexe", "en": "Sex"},
    "sim.nuit": {"fr": "La nuit", "en": "At night"},
    "sim.pluie": {"fr": "Sous la pluie", "en": "In the rain"},
    "sim.hors": {"fr": "Hors agglomération", "en": "Outside built-up areas"},
    "sim.route": {"fr": "Type de route", "en": "Road type"},
    "sim.resultat": {"fr": "Le risque estimé", "en": "Estimated risk"},
    "sim.vehicule_alt": {"fr": "Illustration du profil d'usager sélectionné",
                         "en": "Illustration of the selected road-user profile"},
    "sim.risque_relatif": {"fr": "Risque relatif", "en": "Relative risk"},
    "sim.proba": {"fr": "Probabilité de blessure grave si impliqué",
                  "en": "Probability of serious injury if involved"},
    "sim.comparer": {"fr": "Comparer à la moyenne", "en": "Compare to the average"},
    "sim.moyenne": {"fr": "Moyenne", "en": "Average"},
    "sim.profil_choisi": {"fr": "Profil choisi", "en": "Chosen profile"},
    "sim.ans": {"fr": "ans", "en": "yrs"},
    "sim.jauge_note": {
        "fr": "Risque relatif : probabilité du profil / part moyenne de blessés graves parmi "
              "les usagers impliqués (×1), échelle logarithmique.",
        "en": "Relative risk: profile probability / average share of seriously injured among "
              "involved users (×1), logarithmic scale."},
}
