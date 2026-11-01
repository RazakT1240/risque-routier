"""Scène 08 — Méthode et données : sources, définitions, corrections, limites, table des données."""

from __future__ import annotations

import dash
import dash_ag_grid as dag
import dash_mantine_components as dmc
from dash import Input, Output, callback, html
from dash_iconify import DashIconify

from app import data_access as da
from app.components.blocks import scene_header, scene_layout, scene_nav
from app.components.format import fmt_number
from app.scenes import voisines
from pipeline import config as C

dash.register_page(__name__, path="/methode", name="Méthode et données", order=8,
                   title="Méthode et données · Risque routier")
NUM = 8

SOURCES = [
    ("ONISR — Bases de données annuelles des accidents corporels (BAAC) 2019–2025",
     "Caractéristiques, lieux, véhicules et usagers de chaque accident corporel.",
     "https://www.data.gouv.fr"),
    ("INSEE — Estimations de population au 1er janvier, par département, sexe et âge",
     "Exposition pour les taux par habitant (personnes-années).", "https://www.insee.fr"),
    ("SDES — Parc de véhicules en circulation au 1er janvier",
     "Exposition par groupe de véhicules (pas de deux-roues motorisés).",
     "https://www.statistiques.developpement-durable.gouv.fr"),
    ("Météo-France — Données climatologiques quotidiennes",
     "Pluie, gel et température agrégés par département et par jour.", "https://www.data.gouv.fr"),
    ("Contours des départements (france-geojson)", "Fond de carte simplifié, 96 départements.",
     "https://github.com/gregoiredavid/france-geojson"),
]

DEFINITIONS = [
    ("Victime", "Usager tué, blessé hospitalisé ou blessé léger."),
    ("Tué", "Décès dans les 30 jours qui suivent l'accident."),
    ("Blessé hospitalisé", "Hospitalisé plus de 24 heures. Indicateur non labellisé par la "
                           "statistique publique depuis 2019 : utilisable pour des comparaisons "
                           "internes à la période."),
    ("Létalité", "Tués pour 100 victimes."),
    ("Taux de gravité", "(Tués + hospitalisés) / victimes, en %."),
    ("Victimes pour 100 000 hab.", "Victimes / population × 100 000 ; sur plusieurs années, la "
                                    "population est la somme des populations annuelles."),
    ("Tués par million d'hab.", "Tués / population × 1 000 000."),
    ("Base 100", "Valeur de l'année / valeur 2019 × 100."),
    ("Risque relatif", "Exponentielle d'un coefficient de modèle, avec intervalle de confiance à "
                       "95 % (« × 1,32 »)."),
    ("Seuil d'effectif", f"Un taux calculé sur moins de {C.SEUIL_EFFECTIF} victimes n'est pas "
                         "affiché."),
]

CORRECTIONS = [
    "Tous les fichiers BAAC sont lus en texte puis convertis explicitement ; espaces en tête "
    "(« -1 » précédé d'une espace) et valeurs « N/A » nettoyés.",
    "2022 : la clé « Accident_Id » des caractéristiques est renommée « Num_Acc ».",
    "2019–2020 : identifiant d'usager créé (numéro d'accident + rang).",
    "2025 : nom de colonne « id_vehicule » coupé par un retour à la ligne, nettoyé ; 11 colonnes "
    "identiques à 2024 vérifiées.",
    "2019 : codes département sans zéro initial complétés (« 1 » → « 01 »).",
    "Latitude et longitude : virgule décimale convertie.",
    "Codes « -1 » (et « 0 » quand la notice dit « non renseigné ») traités comme manquants.",
    "Lieux : une seule ligne gardée par accident (doublons présents de 2023 à 2025).",
    "Vitesse maximale autorisée : seules les valeurs réglementaires sont gardées.",
    "Usagers en fuite (depuis 2021) : exclus des calculs qui demandent leur âge, leur sexe ou leur "
    "gravité, comptés dans les contrôles.",
    "Météo : la Corse (« 20 ») est dupliquée en 2A et 2B.",
]

LIMITES = [
    "Pas de données d'assurance : le coût socio-économique n'est pas le coût pour un assureur.",
    "Seuls les accidents corporels constatés par les forces de l'ordre sont recensés ; les "
    "blessés légers sont sous-déclarés.",
    "Exposition approchée par la population et le parc, faute de kilomètres parcourus ; pas de "
    "parc de deux-roues motorisés par département.",
    "Météo moyennée par département et par jour.",
    "Corrélation n'est pas causalité : les modèles décrivent des associations.",
    "2020 est atypique (confinements).",
    "L'indicateur « blessé hospitalisé » n'est plus labellisé depuis 2019.",
    "Depuis 2021, les usagers en fuite ont un sexe, un âge et parfois une gravité inconnus.",
    "Les populations 2024 et 2025 de l'INSEE sont provisoires.",
]

COLONNES = [
    ("annee", "Année", None, 0), ("dep", "Code", None, None),
    ("nom_dep", "Département", None, None),
    ("accidents", "Accidents", "Nombre d'accidents corporels.", 0),
    ("victimes", "Victimes", "Tués + blessés hospitalisés + blessés légers.", 0),
    ("tues", "Tués", "Décès dans les 30 jours.", 0),
    ("hospitalises", "Hospitalisés", "Hospitalisés plus de 24 h (non labellisé depuis 2019).", 0),
    ("legers", "Légers", "Blessés soignés sans hospitalisation de plus de 24 h.", 0),
    ("population", "Population", "Population au 1er janvier (INSEE).", 0),
    ("taux_victimes_100k", "Victimes / 100 000 hab.", "Masqué sous 30 victimes.", 1),
    ("taux_tues_million", "Tués / million d'hab.", "Masqué sous 30 tués.", 1),
    ("taux_letalite", "Létalité", "Tués pour 100 victimes ; masqué sous 30 victimes.", 1),
    ("taux_gravite", "Taux de gravité (%)", "(Tués + hospitalisés) / victimes ; masqué sous 30 "
                                            "victimes.", 1),
]


def _formateur(decimals):
    if decimals is None:
        return None
    return {"function": (f"params.value == null ? '—' : Number(params.value).toLocaleString("
                         f"'fr-FR', {{minimumFractionDigits: {decimals}, "
                         f"maximumFractionDigits: {decimals}}})")}


def grille():
    df = da.table("s08_donnees")
    cols = [c for c, *_ in COLONNES]
    lignes = df[cols + ["metropole"]].copy()
    lignes["perimetre"] = lignes["metropole"].map({True: "Métropole", False: "Outre-mer"})
    lignes = lignes.drop(columns="metropole")
    defs = []
    for col, titre_c, aide, dec in COLONNES:
        d = {"field": col, "headerName": titre_c, "headerTooltip": aide or titre_c,
             "filter": True, "sortable": True}
        if col in ("annee", "dep"):
            d.update(pinned="left", width=96, flex=0)
        elif col == "nom_dep":
            d.update(pinned="left", width=200, flex=0)
        if dec is not None and col != "annee":
            d["valueFormatter"] = _formateur(dec)
            d["type"] = "rightAligned"
            d["filter"] = "agNumberColumnFilter"
        if col.startswith("taux_"):
            d["tooltipValueGetter"] = {"function": "params.value == null ? 'Donnée indisponible "
                                                   ": effectif trop faible ou population "
                                                   "inconnue' : null"}
        defs.append(d)
    defs.insert(3, {"field": "perimetre", "headerName": "Périmètre", "filter": True,
                    "headerTooltip": "Les cartes et taux des autres scènes portent sur la "
                                     "métropole ; l'outre-mer n'apparaît qu'ici."})
    return dag.AgGrid(
        id="s08-grille", rowData=lignes.to_dict("records"), columnDefs=defs,
        defaultColDef={"resizable": True, "flex": 1, "minWidth": 130, "wrapHeaderText": True,
                       "autoHeaderHeight": True},
        className="grille-donnees", style={"height": "560px"},
        dashGridOptions={"pagination": True, "paginationPageSize": 50, "tooltipShowDelay": 200,
                         "localeText": LOCALE_FR, "enableCellTextSelection": True},
        csvExportParams={"fileName": "risque_routier_departements_2019_2025.csv",
                         "columnSeparator": ";"})


LOCALE_FR = {
    "page": "Page", "of": "sur", "to": "à", "more": "plus", "next": "Suivante",
    "previous": "Précédente", "first": "Première", "last": "Dernière", "pageSizeSelectorLabel":
    "Lignes par page :", "filterOoo": "Filtrer…", "equals": "Égal à", "notEqual": "Différent de",
    "lessThan": "Inférieur à", "greaterThan": "Supérieur à", "lessThanOrEqual": "Inférieur ou égal",
    "greaterThanOrEqual": "Supérieur ou égal", "inRange": "Entre", "contains": "Contient",
    "notContains": "Ne contient pas", "startsWith": "Commence par", "endsWith": "Finit par",
    "blank": "Vide", "notBlank": "Non vide", "andCondition": "ET", "orCondition": "OU",
    "noRowsToShow": "Aucune ligne", "loadingOoo": "Chargement…", "applyFilter": "Appliquer",
    "resetFilter": "Réinitialiser", "clearFilter": "Effacer", "inRangeStart": "De",
    "inRangeEnd": "À", "ariaPageSizeSelectorLabel": "Lignes par page",
}


def typo(texte: str) -> str:
    """Guillemets français insécables : jamais de « ou » isolé en bout de ligne."""
    return texte.replace("« ", "« ").replace(" »", " »")


def liste(items):
    return html.Ul(className="body liste-methode", children=[html.Li(typo(i)) for i in items])


def bloc(titre_b, icone, contenu):
    return html.Section(className="carte", children=dmc.Stack(gap=12, children=[
        dmc.Group(gap=8, children=[DashIconify(icon=icone, width=20, className="t-accent"),
                                   html.H2(titre_b, className="h2")]),
        contenu]))


def controles():
    df = da.table("s08_donnees")
    met = df[df["metropole"]].groupby("annee")[["accidents", "victimes", "tues"]].sum()
    tete = ["Année", "Accidents", "Victimes", "Tués"]
    corps = [[str(a), fmt_number(r["accidents"]), fmt_number(r["victimes"]), fmt_number(r["tues"])]
             for a, r in met.iterrows()]
    return html.Div([
        html.P("Totaux annuels calculés depuis les fichiers BAAC (France métropolitaine), à "
               "comparer aux bilans annuels de l'ONISR.", className="body"),
        dmc.Table(striped=True, data={"head": tete, "body": corps}),
    ])


def layout(**_):
    references = da.references() or {}
    vt = references.get("valeurs_tutelaires_eur") or {}
    a_renseigner = "À renseigner"
    methode = dmc.Stack(gap=24, children=[
        bloc("Sources", "tabler:database", html.Ul(className="body liste-methode", children=[
            html.Li([html.A(nom, href=url, target="_blank", rel="noopener noreferrer",
                            className="t-accent"), html.Br(), html.Span(desc, className="caption")])
            for nom, desc, url in SOURCES])),
        html.Div(className="grille-2", children=[
            bloc("Définitions", "tabler:book", html.Dl(className="definitions", children=[
                x for terme, d in DEFINITIONS for x in (html.Dt(terme), html.Dd(typo(d)))])),
            bloc("Corrections appliquées aux données", "tabler:tool", liste(CORRECTIONS)),
        ]),
        html.Div(className="grille-2", children=[
            bloc("Limites", "tabler:alert-circle", liste(LIMITES)),
            bloc("Contrôles de cohérence", "tabler:checks", controles()),
        ]),
        bloc("Valeurs externes", "tabler:file-certificate", html.Div([
            html.P("Ces valeurs ne sont pas dans les données fournies. Les valeurs tutélaires "
                   "ci-dessous sont les valeurs officielles de l'ONISR (méthode Quinet) ; "
                   + ("elles restent à confirmer par le propriétaire."
                      if not vt.get("verifie") else "elles ont été confirmées."),
                   className="body"),
            dmc.Table(data={"head": ["Valeur", "Montant", "Source"], "body": [
                ["Coût d'un tué (valeur tutélaire)",
                 fmt_number(vt["tue"]) + " €" if vt.get("tue") else a_renseigner,
                 vt.get("source") or a_renseigner],
                ["Coût d'un blessé hospitalisé",
                 fmt_number(vt["blesse_hospitalise"]) + " €" if vt.get("blesse_hospitalise")
                 else a_renseigner, vt.get("source") or a_renseigner],
                ["Coût d'un blessé léger",
                 fmt_number(vt["blesse_leger"]) + " €" if vt.get("blesse_leger")
                 else a_renseigner, vt.get("source") or a_renseigner],
                ["Part des 2RM dans le trafic", references.get("part_trafic_2rm_pct")
                 or a_renseigner, references.get("part_trafic_2rm_source") or a_renseigner],
            ]}),
        ])),
    ])
    donnees = dmc.Stack(gap=16, children=[
        dmc.Group(justify="space-between", children=[
            html.P("Indicateurs par département et par année (outre-mer compris). Survolez un "
                   "en-tête pour sa définition ; « — » signale un taux masqué (effectif trop "
                   "faible) ou une population inconnue.", className="body recit",
                   style={"margin": 0}),
            dmc.Button("Exporter en CSV", id="s08-export", variant="light",
                       leftSection=DashIconify(icon="tabler:download", width=16)),
        ]),
        grille(),
    ])
    return scene_layout(
        scene_header(NUM, "Méthode et données", "Chaque chiffre vient des données,",
                     "et se vérifie.", "Sources, définitions, corrections, limites et table "
                                       "complète des indicateurs par département."),
        dmc.Tabs(value="methode", children=[
            dmc.TabsList([dmc.TabsTab("Méthode", value="methode",
                                      leftSection=DashIconify(icon="tabler:book-2", width=16)),
                          dmc.TabsTab("Données", value="donnees",
                                      leftSection=DashIconify(icon="tabler:table", width=16))]),
            dmc.TabsPanel(methode, value="methode", pt="lg"),
            dmc.TabsPanel(donnees, value="donnees", pt="lg"),
        ]),
        scene_nav(*voisines(NUM)),
    )


@callback(Output("s08-grille", "exportDataAsCsv"), Input("s08-export", "n_clicks"),
          prevent_initial_call=True)
def exporter(_):
    return True


@callback(Output("s08-grille", "className"), Input("theme-toggle", "computedColorScheme"))
def theme_grille(scheme):
    return "grille-donnees grille-sombre" if scheme == "dark" else "grille-donnees"
