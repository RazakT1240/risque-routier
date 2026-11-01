"""Scène 04 — Qui : quels profils cumulent fréquence et gravité ?"""

from __future__ import annotations

import dash
import numpy as np
import pandas as pd
from dash import Output, callback, html

from app import data_access as da
from app import figures as F
from app.components.blocks import insight, scene_header, scene_layout, scene_nav
from app.components.chart_card import chart_card, chip_filtre, graph_id
from app.components.format import fmt_number, fmt_pct, fmt_ratio
from app.components.kpi_card import kpi_card, kpi_row
from app.components.scene_utils import ENTREES, SEUIL, deltas_annuels, fmt_ou_na, lire
from app.scenes import voisines
from pipeline import config as C
from pipeline.indicators import letalite, pour_100k, taux_gravite

dash.register_page(__name__, path="/qui", name="Qui", order=4, title="Qui · Risque routier")
NUM = 4
AGES_65 = [c for c in C.CLASSES_AGE if c == "95+" or int(c.split("-")[0]) >= 65]
JEUNES = {"15-19", "20-24", "25-29"}


def taux_age(periode, dep) -> pd.DataFrame:
    """Victimes graves pour 100 000 hab. par sexe × classe d'âge (masqué sous le seuil)."""
    s = da.filtrer(da.table("s04_age"), periode, dep).groupby(
        ["sexe_lib", "classe_age"], observed=True)[["graves", "tues"]].sum().reset_index()
    pop = da.filtrer(da.table("expo_population"), periode, dep).groupby(
        ["sexe", "classe_age"], observed=True)["population"].sum().reset_index().rename(
        columns={"sexe": "sexe_lib"})
    m = pop.merge(s, on=["sexe_lib", "classe_age"], how="left").fillna({"graves": 0, "tues": 0})
    m["taux"] = pour_100k(m["graves"], m["population"]).where(m["graves"] >= SEUIL)
    m["classe_age"] = pd.Categorical(m["classe_age"].astype(str), categories=C.CLASSES_AGE)
    return m.sort_values("classe_age")


def par_type(periode, dep) -> pd.DataFrame:
    g = da.filtrer(da.table("s02_gravite"), periode, dep).groupby(
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


def titre():
    pic, g, _ = _national()
    tete = type_en_tete(g)
    if pic["sexe_lib"] == "Homme" and str(pic["classe_age"]) in JEUNES and tete == "2RM":
        return ("Les jeunes hommes et les deux-roues", "concentrent les blessures graves.")
    sexe = "hommes" if pic["sexe_lib"] == "Homme" else "femmes"
    return (f"Les {sexe} de {str(pic['classe_age']).replace('-', '–')} ans",
            "concentrent les blessures graves.")


def chapeau():
    pic, g, ratio = _national()
    return (f"Rapportées à la population, les blessures graves culminent chez les "
            f"{'hommes' if pic['sexe_lib'] == 'Homme' else 'femmes'} de "
            f"{str(pic['classe_age']).replace('-', '–')} ans "
            f"({fmt_number(pic['taux'], 0)} pour 100 000 habitants et par an"
            + (f", {fmt_number(ratio, 1)} fois plus que les femmes du même âge)." if ratio
               else ")."))


def et_alors():
    _, g, _ = _national()
    tete = type_en_tete(g)
    voiture = g.loc["Voiture", "gravite"] if "Voiture" in g.index else None
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
        scene_header(NUM, "Qui", debut, accent, chapeau()),
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
        insight(et_alors()),
        scene_nav(*voisines(NUM)),
    )


def _series(dep):
    """Séries annuelles des quatre KPI (pour les mini-courbes et les variations)."""
    ratio, part2rm, part65 = [], [], []
    for a in C.ANNEES:
        s = da.filtrer(da.table("s04_age"), str(a), dep)
        pop = da.filtrer(da.table("expo_population"), str(a), dep).groupby("sexe")[
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
    s = da.filtrer(da.table("s04_age"), periode, dep)
    pop = da.filtrer(da.table("expo_population"), periode, dep).groupby("sexe")["population"].sum()
    src = f"Source : {da.SOURCE_BAAC} ; {da.SOURCE_INSEE} · {da.libelle_territoire(dep)}."

    # 1. Classe d'âge au taux de victimes graves le plus élevé
    if len(valides):
        pic = valides.loc[valides["taux"].idxmax()]
        k1 = kpi_card("s04-k1", "Âge le plus exposé", "tabler:user-exclamation",
                      f"{str(pic['classe_age']).replace('-', '–')} ans", texte=True,
                      deltas=[{"texte": f"{fmt_number(pic['taux'], 0)} victimes graves "
                                        "/ 100 000 hab.", "sens": "neutre"}],
                      leader=("tabler:gender-bigender",
                              [f"{'Hommes' if pic['sexe_lib'] == 'Homme' else 'Femmes'}",
                               " de cette classe d'âge"]),
                      lire="Classe d'âge et sexe où les blessures graves sont les plus "
                           "fréquentes, rapportées à la population.",
                      assureur="L'âge du conducteur reste un marqueur de gravité, pas seulement "
                               "de fréquence.", source=src)
    else:
        k1 = kpi_card("s04-k1", "Âge le plus exposé", "tabler:user-exclamation", "—",
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
                  assureur="Le sexe, interdit en tarification depuis 2012, reste un fort "
                           "marqueur de risque à expliquer par l'usage.", source=src,
                  indisponible=ratio is None)

    # 3. Part des 2RM parmi les tués
    tt = s.groupby("type_usager", observed=True)["tues"].sum()
    part2rm = tt.get("2RM", 0) / tt.sum() * 100 if tt.sum() >= SEUIL else None
    casque = da.filtrer(da.table("s04_casque"), periode, dep).groupby(
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
