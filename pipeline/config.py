"""Constantes du pipeline : chemins, années, seuils et tables de codes.

Les codes BAAC ont été vérifiés dans docs/description-des-bases-de-donnees-annuelles.pdf
(ONISR, 21/10/2026) le 01/11/2026 (garde-fou G2). Indépendant de Dash.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW_BAAC = DATA / "baac"
RAW_METEO = DATA / "meteo" / "meteo_dep_jour_2019_2025.csv"
RAW_INSEE = DATA / "insee" / "insee_estim-pop-dep-sexe-aq-1975-2026.xlsx"
RAW_SDES = DATA / "sdes" / "sdes_parc_vehicules_dep_2019_2026.csv"
RAW_GEO = DATA / "geo" / "departements-version-simplifiee.geojson"
RAW_GEO_OM = DATA / "geo" / "departements-avec-outre-mer.geojson"
PROCESSED = DATA / "processed"
MODELS = PROCESSED / "models"
REFERENCES = ROOT / "config" / "references.yaml"
REPORTS = ROOT / "reports"

ANNEES = list(range(2019, 2026))
ANNEE_REF = 2019            # base 100
TABLES_BAAC = ("caract", "lieux", "vehicules", "usagers")

# G6 : un taux calculé sur moins de SEUIL_EFFECTIF victimes n'est pas affiché
SEUIL_EFFECTIF = 30

# Codes DOM / COM présents dans les BAAC : hors périmètre des cartes et des taux
DEP_OUTRE_MER = {"971", "972", "973", "974", "975", "976", "977", "978", "986", "987", "988"}

# Colonnes codées converties en entier ; "-1" -> manquant partout
COLS_CODES = {
    "caract": ["jour", "mois", "an", "lum", "agg", "int", "atm", "col"],
    "lieux": ["catr", "circ", "nbv", "vosp", "prof", "plan", "surf", "infra", "situ", "vma"],
    "vehicules": ["senc", "catv", "obs", "obsm", "choc", "manv", "motor", "occutc"],
    "usagers": ["place", "catu", "grav", "sexe", "an_nais", "trajet", "secu1", "secu2",
                "secu3", "locp", "etatp"],
}
# Colonnes où 0 signifie « non renseigné / inconnu » d'après le PDF
COLS_ZERO_MANQUANT = {"vehicules": ["senc", "manv", "motor"], "usagers": ["trajet"]}
# actp contient des lettres (A, B) : reste en texte ; "-1" et "0" = non renseigné
ACTP_MANQUANT = {"-1", "0"}

COLS_VEHICULES_2025 = ["Num_Acc", "id_vehicule", "num_veh", "senc", "catv", "obs", "obsm",
                       "choc", "manv", "motor", "occutc"]

VMA_VALIDES = {10, 20, 30, 40, 50, 60, 70, 80, 90, 110, 130}
AGE_MIN, AGE_MAX = 0, 110

# --- Libellés (PDF ONISR) -------------------------------------------------
GRAV = {1: "Indemne", 2: "Tué", 3: "Blessé hospitalisé", 4: "Blessé léger"}
CATU = {1: "Conducteur", 2: "Passager", 3: "Piéton"}
SEXE = {1: "Homme", 2: "Femme"}
AGG = {1: "Hors agglomération", 2: "En agglomération"}
LUM = {1: "Plein jour", 2: "Crépuscule ou aube", 3: "Nuit sans éclairage public",
       4: "Nuit avec éclairage public non allumé", 5: "Nuit avec éclairage public allumé"}
CATR = {1: "Autoroute", 2: "Route nationale", 3: "Route départementale", 4: "Voie communale",
        5: "Hors réseau public", 6: "Parc de stationnement", 7: "Route de métropole urbaine",
        9: "Autre"}

# Regroupements pour l'affichage
CATR_GROUPE = {1: "Autoroute", 2: "Nationale", 3: "Départementale", 4: "Communale",
               7: "Métropole urbaine", 5: "Autre", 6: "Autre", 9: "Autre"}
CATR_GROUPE_ORDRE = ["Autoroute", "Nationale", "Départementale", "Communale",
                     "Métropole urbaine", "Autre"]
LUM_GROUPE = {1: "Jour", 2: "Aube ou crépuscule", 5: "Nuit éclairée",
              3: "Nuit non éclairée", 4: "Nuit non éclairée"}
LUM_GROUPE_ORDRE = ["Jour", "Aube ou crépuscule", "Nuit éclairée", "Nuit non éclairée"]
NUIT_LUM = {3, 4, 5}

# Obstacle fixe heurté (obs) : regroupement des 18 modalités du PDF
OBS_GROUPE = {0: "Aucun obstacle fixe", 2: "Arbre", 13: "Fossé, talus, paroi rocheuse",
              3: "Glissière", 4: "Glissière", 5: "Glissière",
              6: "Bâtiment, mur, pile de pont", 7: "Poteau, support", 8: "Poteau, support",
              16: "Sortie de chaussée sans obstacle"}
OBS_AUTRE = "Autre obstacle fixe"   # 1, 9, 10, 11, 12, 14, 15, 17
OBS_GROUPE_ORDRE = ["Aucun obstacle fixe", "Sortie de chaussée sans obstacle", "Arbre",
                    "Fossé, talus, paroi rocheuse", "Glissière",
                    "Bâtiment, mur, pile de pont", "Poteau, support", OBS_AUTRE]

SECU_CASQUE = 2
CASQUE_ORDRE = ["Casque", "Aucun équipement", "Indéterminé"]

# type_usager : piéton d'abord (catu == 3), sinon d'après le catv du véhicule de l'usager
TYPE_USAGER_CATV = {
    "Vélo": {1, 80},
    "EDP": {50, 60},
    "2RM": {2, 30, 31, 32, 33, 34, 41, 42, 43},
    "Voiture": {3, 7},
    "Utilitaire": {10},
    "Poids lourd": {13, 14, 15, 16, 17},
    "Bus, car, tram": {37, 38, 39, 40},
}
TYPE_USAGER_ORDRE = ["Piéton", "Vélo", "EDP", "2RM", "Voiture", "Utilitaire", "Poids lourd",
                     "Bus, car, tram", "Autre"]

# Groupes du parc SDES <-> type de véhicule BAAC (exposition, G5)
GROUPE_PARC_CATV = {"VP": {7},"VUL": {10}, "PL": {13, 14, 15, 16, 17}, "TCP": {37, 38}}

# Classes d'âge alignées sur l'INSEE (quinquennales)
CLASSES_AGE = [f"{a}-{a + 4}" for a in range(0, 95, 5)] + ["95+"]

JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

# --- Météo ---------------------------------------------------------------
METEO_SEC_MAX_MM = 0.2          # sec : rr_moy < 0,2 mm
METEO_PLUIE_FORTE_MM = 5.0      # pluie forte : rr_moy >= 5 mm
METEO_GEL_PART = 0.5            # gel : part des stations avec TN <= 0 °C >= 0,5
PLUIE_JOUR_MM = 1.0             # jour de pluie pour « première pluie »
PREMIERE_PLUIE_JOURS_SECS = 7
METEO_CAT_ORDRE = ["sec", "pluie faible", "pluie forte", "gel"]
