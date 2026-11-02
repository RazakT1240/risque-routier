"""Scène 04 — Qui : quels profils cumulent fréquence et gravité ?"""

from __future__ import annotations

import dash
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
from dash import Input, Output, callback, html

from app import data_access as da
from app import echarts as E
from app import figures as F
from app import i18n
from app.components.blocks import insight, scene_header, scene_layout, scene_nav
from app.components.chart_card import chart_card, chip_filtre, echart_id, graph_id
from app.components.format import fmt_number, fmt_pct, fmt_ratio
from app.components.kpi_card import kpi_card, kpi_row
from app.components.scene_utils import ENTREES, SEUIL, deltas_annuels, fmt_ou_na, lire
from app.scenes import voisines
from design.tokens import tokens
from pipeline import config as C
from pipeline.indicators import letalite, pour_100k, taux_gravite

dash.register_page(__name__, path="/qui", name="Qui", order=4, title="Qui · Risque routier")
NUM = 4
AGES_65 = [c for c in C.CLASSES_AGE if c == "95+" or int(c.split("-")[0]) >= 65]
JEUNES = {"15-19", "20-24", "25-29"}


def taux_age(periode, dep) -> pd.DataFrame:
    """Victimes graves pour 100 000 hab. par sexe × classe d'âge (masqué sous le seuil)."""
    s = da.filtre_table("s04_age", periode, dep).groupby(
        ["sexe_lib", "classe_age"], observed=True)[["graves", "tues"]].sum().reset_index()
    pop = da.filtre_table("expo_population", periode, dep).groupby(
        ["sexe", "classe_age"], observed=True)["population"].sum().reset_index().rename(
        columns={"sexe": "sexe_lib"})
    m = pop.merge(s, on=["sexe_lib", "classe_age"], how="left").fillna({"graves": 0, "tues": 0})
    m["taux"] = pour_100k(m["graves"], m["population"]).where(m["graves"] >= SEUIL)
    m["classe_age"] = pd.Categorical(m["classe_age"].astype(str), categories=C.CLASSES_AGE)
    return m.sort_values("classe_age")


def par_type(periode, dep) -> pd.DataFrame:
    g = da.filtre_table("s02_gravite", periode, dep).groupby(
        "type_usager", observed=True)[["victimes", "tues", "hospitalises", "graves"]].sum()
    # Parts calculées sur l'ensemble des victimes, avant d'écarter « Autre » et les petits types
    g["part_victimes"] = g["victimes"] / g["victimes"].sum() * 100
    g["gravite"] = taux_gravite(g["tues"], g["hospitalises"], g["victimes"])
    return g[(g["victimes"] >= SEUIL) & (g.index != "Autre")]


def type_en_tete(g: pd.DataFrame) -> str | None:
    """Type le plus grave parmi ceux qui pèsent au moins 5 % des victimes."""
    gros = g[g["part_victimes"] >= 5]
    return gros["gravite"].idxmax() if len(gros) else None


def _national():
    m = taux_age(da.PERIODE_CUMUL, da.TERRITOIRE_FRANCE).dropna(subset=["taux"])
    pic = m.loc[m["taux"].idxmax()]
    g = par_type(da.PERIODE_CUMUL, da.TERRITOIRE_FRANCE)
    femmes = m[(m["sexe_lib"] == "Femme") & (m["classe_age"] == pic["classe_age"])]["taux"]
    return pic, g, (pic["taux"] / femmes.iloc[0]) if len(femmes) else None


# Personne-usager en anglais (pour l'encart « Et alors ? »), valeur de données -> libellé EN
_VEH_EN = {"2RM": "motorcyclist", "Vélo": "cyclist", "Piéton": "pedestrian",
           "EDP": "e-scooter rider", "Voiture": "car occupant", "Utilitaire": "van occupant",
           "Poids lourd": "truck occupant", "Bus, car, tram": "bus passenger",
           "Autre": "other-vehicle user"}


def titre():
    pic, g, _ = _national()
    tete = type_en_tete(g)
    en = i18n.langue() == "en"
    classe = str(pic["classe_age"]).replace("-", "–")
    homme = pic["sexe_lib"] == "Homme"
    if homme and str(pic["classe_age"]) in JEUNES and tete == "2RM":
        return (("Young men and powered two-wheelers", "are the most exposed to serious injury.")
                if en else
                ("Les jeunes hommes et les deux-roues", "sont les plus exposés aux blessures "
                 "graves."))
    if en:
        return (f"{'Men' if homme else 'Women'} aged {classe}",
                "are the most exposed to serious injury.")
    return (f"Les {'hommes' if homme else 'femmes'} de {classe} ans",
            "sont les plus exposés aux blessures graves.")


def chapeau():
    pic, g, ratio = _national()
    classe = str(pic["classe_age"]).replace("-", "–")
    homme = pic["sexe_lib"] == "Homme"
    taux = fmt_number(pic["taux"], 0)
    if i18n.langue() == "en":
        plus = (f", {fmt_number(ratio, 1)} times the rate of women the same age)." if ratio
                else ").")
        return (f"Relative to population, serious injuries peak among "
                f"{'men' if homme else 'women'} aged {classe} "
                f"({taux} per 100,000 inhabitants per year" + plus)
    plus = (f", {fmt_number(ratio, 1)} fois plus que les femmes du même âge)." if ratio
            else ").")
    return (f"Rapportées à la population, les blessures graves culminent chez les "
            f"{'hommes' if homme else 'femmes'} de {classe} ans "
            f"({taux} pour 100 000 habitants et par an" + plus)


def et_alors():
    _, g, _ = _national()
    tete = type_en_tete(g)
    voiture = g.loc["Voiture", "gravite"] if "Voiture" in g.index else None
    en = i18n.langue() == "en"
    if en:
        phrase = ""
        if tete and voiture is not None:
            phrase = (f" A {_VEH_EN.get(tete, tete)} is killed or hospitalised in "
                      f"{fmt_pct(g.loc[tete, 'gravite'], 0)} of cases, versus "
                      f"{fmt_pct(voiture, 0)} for a car occupant.")
        return ("Age and vehicle type strongly shape injury severity: two variables that pricing "
                "already knows how to observe." + phrase)
    phrase = ""
    if tete and voiture is not None:
        phrase = (f" Une victime {'en 2RM' if tete == '2RM' else tete.lower()} est tuée ou "
                  f"hospitalisée dans {fmt_pct(g.loc[tete, 'gravite'], 0)} des cas, contre "
                  f"{fmt_pct(voiture, 0)} en voiture.")
    return ("L'âge et le type de véhicule marquent fortement la gravité des blessures : deux "
            "variables que la tarification sait déjà observer." + phrase)


def layout(**_):
    debut, accent = titre()
    return scene_layout(
        scene_header(NUM, i18n.nom_scene("/qui"), debut, accent, chapeau()),
        html.Div(id="s04-kpis"),
        html.Div(className="grille-2", children=[
            chart_card("s04-age", "Victimes graves par âge et par sexe",
                       "Victimes graves (tués et hospitalisés) pour 100 000 habitants, par âge.",
                       f"{da.SOURCE_BAAC} ; {da.SOURCE_INSEE}",
                       "victimes graves / population de la classe d'âge × 100 000, par an ; "
                       "classes sous 30 victimes masquées", hauteur=360),
            chart_card("s04-matrice", "Quels usagers sont à la fois nombreux et gravement "
                       "touchés ?",
                       "Chaque bulle : un type d'usager. Taille : nombre de tués.",
                       da.SOURCE_BAAC,
                       "part des victimes ; taux de gravité = (tués + hospitalisés) / victimes ; "
                       "types sous 30 victimes exclus", hauteur=360),
        ]),
        html.Div(className="grille-2", children=[
            chart_card("s04-boites", "L'âge des tués selon le mode de déplacement",
                       "Boîte = moitié centrale des âges ; trait = médiane ; losange = moyenne ; "
                       "moustaches = valeurs usuelles.", da.SOURCE_BAAC,
                       "âge au jour de l'accident des usagers tués ; France métropolitaine ; "
                       "modes de moins de 30 tués exclus", hauteur=380),
            chart_card("s04-matrice-age", "Mode × âge : la part des blessures graves",
                       "Part des victimes tuées ou hospitalisées, par mode et tranche d'âge.",
                       da.SOURCE_BAAC, "taux de gravité = (tués + hospitalisés) / victimes ; "
                       "cases sous 30 victimes grisées", hauteur=380),
        ]),
        html.Div(className="grille-2", children=[
            chart_card("s04-pyramide", "La pyramide des âges des tués",
                       "Tués par million d'habitants et par an, hommes à gauche, femmes à droite.",
                       f"{da.SOURCE_BAAC} ; {da.SOURCE_INSEE}",
                       "tués / population de la classe d'âge et du sexe × 1 000 000, par an ; "
                       "classes sous 30 tués non affichées", hauteur=440),
            chart_card("s04-treemap", "Où se concentrent les tués : mode × route",
                       "Surface : nombre de tués ; couleur : létalité (plus foncé = plus mortel).",
                       da.SOURCE_BAAC, "létalité = tués / victimes × 100 ; croisements sous 30 "
                       "victimes exclus", hauteur=440),
        ]),
        html.Div(className="grille-2-1", children=[
            chart_card("s04-radar", "Le contexte aggrave-t-il autant tous les modes ?",
                       "Taux de gravité du mode choisi (rouge) et de l'ensemble des usagers "
                       "(gris), selon le moment et le lieu.", da.SOURCE_BAAC,
                       "taux de gravité = (tués + hospitalisés) / victimes ; contextes sous 30 "
                       "victimes non tracés", hauteur=400, moteur="echarts",
                       controles=dmc.Select(id="s04-mode", data=RADAR_MODES, value="2RM",
                                            allowDeselect=False, w=220,
                                            comboboxProps={"withinPortal": True},
                                            **{"aria-label": "Mode de déplacement"})),
            chart_card("s04-jauge", "Gravité du mode choisi",
                       "Part des victimes tuées ou hospitalisées ; trait : ensemble des "
                       "usagers.", da.SOURCE_BAAC, "taux de gravité = (tués + hospitalisés) / "
                       "victimes", hauteur=300, moteur="echarts"),
        ]),
        insight(et_alors()),
        scene_nav(*voisines(NUM)),
    )


def _series(dep):
    """Séries annuelles des quatre KPI (pour les mini-courbes et les variations)."""
    ratio, part2rm, part65 = [], [], []
    for a in C.ANNEES:
        s = da.filtre_table("s04_age", str(a), dep)
        pop = da.filtre_table("expo_population", str(a), dep).groupby("sexe")[
            "population"].sum()
        th = s[s["sexe_lib"] == "Homme"]["tues"].sum()
        tf = s[s["sexe_lib"] == "Femme"]["tues"].sum()
        ratio.append((th / pop.get("Homme", np.nan)) / (tf / pop.get("Femme", np.nan))
                     if tf >= SEUIL and th >= SEUIL else np.nan)
        tt = s.groupby("type_usager", observed=True)["tues"].sum()
        part2rm.append(tt.get("2RM", 0) / tt.sum() * 100 if tt.sum() >= SEUIL else np.nan)
        pi = s[s["type_usager"] == "Piéton"]
        n = pi["tues"].sum()
        part65.append(pi[pi["classe_age"].astype(str).isin(AGES_65)]["tues"].sum() / n * 100
                      if n >= SEUIL else np.nan)
    idx = pd.Index(C.ANNEES)
    return pd.Series(ratio, idx), pd.Series(part2rm, idx), pd.Series(part65, idx)


@callback(Output("s04-kpis", "children"), *ENTREES)
def kpis(filtres, scheme):
    periode, dep, _ = lire(filtres, scheme)
    m = taux_age(periode, dep)
    valides = m.dropna(subset=["taux"])
    s_ratio, s_2rm, s_65 = _series(dep)
    s = da.filtre_table("s04_age", periode, dep)
    pop = da.filtre_table("expo_population", periode, dep).groupby("sexe")["population"].sum()
    src = f"Source : {da.SOURCE_BAAC} ; {da.SOURCE_INSEE} · {da.libelle_territoire(dep)}."

    # 1. Classe d'âge au taux de victimes graves le plus élevé
    if len(valides):
        pic = valides.loc[valides["taux"].idxmax()]
        k1 = kpi_card("s04-k1", "Âge le plus exposé", "tabler:user-exclamation", vedette=True,
                      valeur=
                      f"{str(pic['classe_age']).replace('-', '–')} ans", texte=True,
                      deltas=[{"texte": f"{fmt_number(pic['taux'], 0)} victimes graves "
                                        "/ 100 000 hab.", "sens": "neutre"}],
                      leader=("tabler:gender-bigender",
                              [f"{'Hommes' if pic['sexe_lib'] == 'Homme' else 'Femmes'}",
                               " de cette classe d'âge"]),
                      lire="Âge et sexe où les blessures graves par habitant sont les plus "
                           "fréquentes.",
                      assureur="L'âge du conducteur reste un marqueur de gravité, pas seulement "
                               "de fréquence.", source=src)
    else:
        k1 = kpi_card("s04-k1", "Âge le plus exposé", "tabler:user-exclamation", vedette=True,
                      valeur= "—",
                      lire="Effectifs trop faibles par classe d'âge sur ce périmètre.",
                      assureur="Élargir la période ou le territoire.", source=src,
                      indisponible=True)

    # 2. Ratio hommes / femmes des tués par habitant
    th, tf = s[s["sexe_lib"] == "Homme"]["tues"].sum(), s[s["sexe_lib"] == "Femme"]["tues"].sum()
    ratio = ((th / pop.get("Homme")) / (tf / pop.get("Femme"))
             if th >= SEUIL and tf >= SEUIL else None)
    k2 = kpi_card("s04-k2", "Tués : hommes / femmes", "tabler:gender-male",
                  fmt_ratio(ratio, 1) if ratio else "—",
                  deltas=deltas_annuels(s_ratio, periode, None) if ratio else [],
                  leader=("tabler:man", ["Hommes : ", html.B(fmt_number(
                      th / pop.get("Homme") * 1e6, 0)), " tués / million"]) if ratio else None,
                  spark=s_ratio.tolist(),
                  lire="Taux de tués par habitant des hommes divisé par celui des femmes.",
                  assureur="Le sexe, exclu des tarifs depuis 2012, reste un marqueur à "
                           "expliquer par l'usage.", source=src,
                  indisponible=ratio is None)

    # 3. Part des 2RM parmi les tués
    tt = s.groupby("type_usager", observed=True)["tues"].sum()
    part2rm = tt.get("2RM", 0) / tt.sum() * 100 if tt.sum() >= SEUIL else None
    casque = da.filtre_table("s04_casque", periode, dep).groupby(
        "casque", observed=True)[["tues", "victimes"]].sum()
    leader3 = None
    if "Aucun équipement" in casque.index and casque.loc["Aucun équipement", "victimes"] >= SEUIL:
        lc = letalite(casque.loc["Aucun équipement", "tues"],
                      casque.loc["Aucun équipement", "victimes"])
        leader3 = ("tabler:helmet-off", ["Sans équipement : létalité ", html.B(fmt_number(lc, 1))])
    k3 = kpi_card("s04-k3", "Part des 2RM (tués)", "tabler:motorbike",
                  fmt_ou_na(part2rm, 1, pct=True),
                  deltas=deltas_annuels(s_2rm, periode, None, points=True) if part2rm else [],
                  leader=leader3, spark=s_2rm.tolist(),
                  lire="Part des usagers de deux-roues motorisés (cyclos, scooters, motos) parmi "
                       "les tués.", assureur="À rapprocher de la part des 2RM dans le trafic : "
                  f"{(da.references() or {}).get('part_trafic_2rm_pct') or 'À renseigner'} "
                  "(voir Méthode).", source=src,
                  indisponible=part2rm is None)

    # 4. Part des 65 ans et plus parmi les piétons tués
    pi = s[s["type_usager"] == "Piéton"]
    n = pi["tues"].sum()
    n65 = pi[pi["classe_age"].astype(str).isin(AGES_65)]["tues"].sum()
    part65 = n65 / n * 100 if n >= SEUIL else None
    k4 = kpi_card("s04-k4", "Piétons tués : 65 ans +", "tabler:walk",
                  fmt_ou_na(part65, 1, pct=True),
                  deltas=deltas_annuels(s_65, periode, None, points=True) if part65 else [],
                  leader=("tabler:walk", [html.B(fmt_number(n65)), " piétons tués de 65 ans "
                                                                    "et plus"]) if part65 else None,
                  spark=s_65.tolist(),
                  lire="Part des 65 ans et plus parmi les piétons tués.",
                  assureur="Un piéton blessé est indemnisé par l'assureur du véhicule : un "
                           "enjeu de responsabilité civile.", source=src,
                  indisponible=part65 is None)
    return kpi_row([k1, k2, k3, k4])


@callback(Output(graph_id("s04-age"), "figure"), Output("s04-age-puces", "children"),
          Output(graph_id("s04-matrice"), "figure"), Output("s04-matrice-puces", "children"),
          Output("s04-age-titre", "children"), *ENTREES)
def graphes(filtres, scheme):
    periode, dep, scheme = lire(filtres, scheme)
    puces = [chip_filtre(x) for x in da.puces_filtres(periode, dep)]
    m = taux_age(periode, dep)
    h = m[m["sexe_lib"] == "Homme"].set_index("classe_age")["taux"]
    f = m[m["sexe_lib"] == "Femme"].set_index("classe_age")["taux"]
    valides = m.dropna(subset=["taux"])
    if len(valides):
        pic = valides.loc[valides["taux"].idxmax()]
        titre_age = (f"Le risque grave culmine chez les "
                     f"{'hommes' if pic['sexe_lib'] == 'Homme' else 'femmes'} de "
                     f"{str(pic['classe_age']).replace('-', '–')} ans")
    else:
        titre_age = "Victimes graves par âge et par sexe"
    if h.notna().sum() + f.notna().sum() == 0:
        fig_age = F.message_figure("Moins de 30 victimes graves par classe : taux non affichés",
                                   scheme)
    else:
        ecart = (h / f).max()
        fig_age = F.courbes_age([str(c) for c in C.CLASSES_AGE],
                                [h.get(c, np.nan) for c in C.CLASSES_AGE],
                                [f.get(c, np.nan) for c in C.CLASSES_AGE], scheme,
                                alerte_hommes=bool(ecart and ecart > 1.5))
    g = par_type(periode, dep)
    if len(g) < 2:
        fig_m = F.message_figure("Effectifs trop faibles par type d'usager", scheme)
    else:
        fig_m = F.matrice_bulles(list(g.index), g["part_victimes"].round(2).tolist(),
                                 g["gravite"].round(2).tolist(), g["tues"].tolist(),
                                 type_en_tete(g), scheme, "Part des victimes",
                                 "Taux de gravité")
    return fig_age, puces, fig_m, puces, titre_age


TRANCHES = {"0–14": ["0-4", "5-9", "10-14"], "15–24": ["15-19", "20-24"],
            "25–34": ["25-29", "30-34"], "35–44": ["35-39", "40-44"],
            "45–54": ["45-49", "50-54"], "55–64": ["55-59", "60-64"],
            "65–74": ["65-69", "70-74"],
            "75 +": ["75-79", "80-84", "85-89", "90-94", "95+"]}
MODES_MATRICE = ["Piéton", "Vélo", "EDP", "2RM", "Voiture", "Utilitaire"]


@callback(Output(graph_id("s04-boites"), "figure"), Output("s04-boites-puces", "children"),
          Output("s04-boites-titre", "children"),
          Output(graph_id("s04-matrice-age"), "figure"),
          Output("s04-matrice-age-puces", "children"),
          Output("s04-matrice-age-titre", "children"), *ENTREES)
def boites_et_matrice(filtres, scheme):
    periode, dep, scheme = lire(filtres, scheme)
    # Boîtes : statistiques nationales précalculées (non additives), période choisie
    b = da.table("s04_age_box")
    lib = da.LIBELLE_PERIODE_CUMUL if periode == da.PERIODE_CUMUL else periode
    b = b[(b["periode"] == lib) & (b["groupe"] == "Tués") & (b["type_usager"] != "Autre")]
    ordre = [x for x in C.TYPE_USAGER_ORDRE if x in set(b["type_usager"])]
    stats = [{"nom": r["type_usager"], **r.to_dict()} for _, r in
             b.set_index("type_usager").loc[ordre].reset_index().iterrows()]
    puces_b = [chip_filtre(f"France métropolitaine · {da.libelle_periode(periode)}")]
    if stats:
        vieux = max(stats, key=lambda s: s["mediane"])
        jeune = min(stats, key=lambda s: s["mediane"])
        fig_b = F.boites(stats, scheme, alerte=vieux["nom"])
        titre_b = (f"Âge médian des tués : {fmt_number(vieux['mediane'], 0)} ans chez les "
                   f"{'piétons' if vieux['nom'] == 'Piéton' else vieux['nom']}, "
                   f"{fmt_number(jeune['mediane'], 0)} ans en {jeune['nom']}")
    else:
        fig_b = F.message_figure("Effectifs trop faibles", scheme)
        titre_b = "L'âge des tués selon le mode de déplacement"
    # Matrice mode × tranche d'âge (taux de gravité), filtrable
    s = da.filtre_table("s04_age", periode, dep)
    vers_tranche = {c: tr for tr, classes in TRANCHES.items() for c in classes}
    agg = (s.assign(tranche=s["classe_age"].astype(str).map(vers_tranche))
           .groupby(["type_usager", "tranche"], observed=True)[["graves", "victimes"]].sum())
    agg = agg.reindex(pd.MultiIndex.from_product([MODES_MATRICE, list(TRANCHES)]),
                      fill_value=0)
    vict = agg["victimes"].to_numpy().reshape(len(MODES_MATRICE), len(TRANCHES))
    grav = agg["graves"].to_numpy().reshape(len(MODES_MATRICE), len(TRANCHES))
    with np.errstate(invalid="ignore", divide="ignore"):
        z = (grav / vict * 100).tolist()
    masque = (vict < SEUIL).tolist()
    puces_m = [chip_filtre(x) for x in da.puces_filtres(periode, dep)]
    if all(all(lm) for lm in masque):
        return (fig_b, puces_b, titre_b,
                F.message_figure("Moins de 30 victimes par case", scheme), puces_m,
                "Mode × âge : la part des blessures graves")
    fig_m = F.matrice(MODES_MATRICE, list(TRANCHES), z, masque, scheme,
                      fmt=lambda v: fmt_number(v, 0), titre_x="Âge (ans)",
                      survol=" % de victimes graves")
    vis = [(z[i][j], MODES_MATRICE[i], list(TRANCHES)[j]) for i in range(len(MODES_MATRICE))
           for j in range(len(TRANCHES)) if not masque[i][j]]
    v, mode, tr = max(vis)
    titre_m = f"{mode}, {tr} ans : {fmt_pct(v, 0)} des victimes tuées ou hospitalisées"
    return fig_b, puces_b, titre_b, fig_m, puces_m, titre_m


QUAND = {"Jour": "le jour", "Nuit": "la nuit", "Semaine": "en semaine",
         "Week-end": "le week-end", "En agglo.": "en agglomération",
         "Hors agglo.": "hors agglomération"}
RADAR_MODES = ["Piéton", "Vélo", "EDP", "2RM", "Voiture", "Utilitaire"]
CONTEXTES = [("Jour", "nuit", False), ("Nuit", "nuit", True), ("Semaine", "weekend", False),
             ("Week-end", "weekend", True), ("En agglo.", "agg_lib", "En agglomération"),
             ("Hors agglo.", "agg_lib", "Hors agglomération")]


def _gravites(df):
    out = []
    for _, col, val in CONTEXTES:
        d = df[df[col] == val][["graves", "victimes"]].sum()
        out.append(float(d["graves"] / d["victimes"] * 100) if d["victimes"] >= SEUIL else None)
    return out


@callback(Output(echart_id("s04-radar"), "data"), Output("s04-radar-puces", "children"),
          Output("s04-radar-titre", "children"), Output(echart_id("s04-jauge"), "data"),
          Output("s04-jauge-puces", "children"), Output("s04-jauge-titre", "children"),
          Input("s04-mode", "value"), *ENTREES)
def radar_et_jauge(mode, filtres, scheme):
    periode, dep, scheme = lire(filtres, scheme)
    mode = mode or "2RM"
    c = da.filtre_table("s04_contexte", periode, dep)
    puces = [chip_filtre(x) for x in da.puces_filtres(periode, dep)]
    tk = tokens(scheme)
    g_mode, g_tous = _gravites(c[c["type_usager"] == mode]), _gravites(c)
    axes = [lib for lib, *_ in CONTEXTES]
    fig_r = E.radar(axes, {mode: g_mode, "Ensemble des usagers": g_tous},
                    {mode: tk["grav-tue"], "Ensemble des usagers": tk["data-neutre"]}, scheme)
    ecarts = [(a, m - e) for a, m, e in zip(axes, g_mode, g_tous, strict=True) if m and e]
    titre_r = "Gravité selon le contexte"
    if ecarts:
        a, e = max(ecarts, key=lambda x: x[1])
        titre_r = (f"{mode} : l'écart de gravité avec la moyenne culmine {QUAND[a]} "
                   f"({fmt_number(e, 0, signe=True)} pts)")
    tot_m = c[c["type_usager"] == mode][["graves", "victimes"]].sum()
    tot = c[["graves", "victimes"]].sum()
    if tot_m["victimes"] < SEUIL or tot["victimes"] < SEUIL:
        fig_j = E.message("Moins de 30 victimes sur ce périmètre", scheme)
        titre_j = f"Gravité : {mode}"
    else:
        gm = tot_m["graves"] / tot_m["victimes"] * 100
        gt = tot["graves"] / tot["victimes"] * 100
        fig_j = E.jauge(gm, gt, 0, 100, scheme, suffixe=" %", lib_ref="ensemble des usagers",
                        decimals=0)
        titre_j = f"{mode} : {fmt_pct(gm, 0)} des victimes gravement atteintes"
    return fig_r, puces, titre_r, fig_j, puces, titre_j


MODES_TREEMAP = ["Voiture", "2RM", "Piéton", "Vélo", "EDP", "Utilitaire", "Poids lourd"]


@callback(Output(graph_id("s04-pyramide"), "figure"), Output("s04-pyramide-puces", "children"),
          Output("s04-pyramide-titre", "children"), Output(graph_id("s04-treemap"), "figure"),
          Output("s04-treemap-puces", "children"), Output("s04-treemap-titre", "children"),
          *ENTREES)
def pyramide_et_treemap(filtres, scheme):
    periode, dep, scheme = lire(filtres, scheme)
    puces = [chip_filtre(x) for x in da.puces_filtres(periode, dep)]
    # Pyramide : tués par million d'habitants, par sexe et classe d'âge
    s = da.filtre_table("s04_age", periode, dep).groupby(
        ["sexe_lib", "classe_age"], observed=True)["tues"].sum()
    pop = da.filtre_table("expo_population", periode, dep).groupby(
        ["sexe", "classe_age"], observed=True)["population"].sum()
    classes = list(reversed(C.CLASSES_AGE))
    def taux(sexe):
        out = []
        for c in classes:
            n = s.get((sexe, c), 0)
            p = pop.get((sexe, c), 0)
            out.append(n / p * 1e6 if p and n >= SEUIL else None)
        return out
    h, f = taux("Homme"), taux("Femme")
    if all(v is None for v in h + f):
        fig_p = F.message_figure("Moins de 30 tués par classe : pyramide non affichée", scheme)
        titre_p = "La pyramide des âges des tués"
    else:
        fig_p = F.pyramide([c.replace("-", "–") for c in classes], h, f, scheme,
                           "tués / million d'hab.")
        valides = [(v, c, "hommes") for v, c in zip(h, classes, strict=True) if v] + \
                  [(v, c, "femmes") for v, c in zip(f, classes, strict=True) if v]
        v, c, qui = max(valides)
        titre_p = (f"Pic chez les {qui} de {c.replace('-', '–')} ans : "
                   f"{fmt_number(v, 0)} tués par million d'habitants et par an")
    # Treemap : tués par mode puis par type de route, couleur = létalité
    g = da.filtre_table("s02_gravite", periode, dep).groupby(
        ["type_usager", "catr_groupe"], observed=True)[["tues", "victimes"]].sum().reset_index()
    g = g[g["type_usager"].astype(str).isin(MODES_TREEMAP) & (g["victimes"] >= SEUIL)
          & (g["tues"] > 0)]
    if g.empty:
        return (fig_p, puces, titre_p,
                F.message_figure("Effectifs trop faibles par croisement", scheme), puces,
                "Où se concentrent les tués : mode × route")
    let = (g["tues"] / g["victimes"] * 100).round(2)
    fig_t = F.treemap(g["type_usager"].astype(str).tolist(), g["catr_groupe"].astype(str).tolist(),
                      g["tues"].astype(float).tolist(), let.tolist(), scheme, "Tués",
                      "Létalité (tués / 100 victimes)")
    top = g.loc[g["tues"].idxmax()]
    titre_t = (f"{top['type_usager']} sur {str(top['catr_groupe']).lower()} : "
               f"{fmt_pct(top['tues'] / g['tues'].sum() * 100, 0)} des tués")
    return fig_p, puces, titre_p, fig_t, puces, titre_t
