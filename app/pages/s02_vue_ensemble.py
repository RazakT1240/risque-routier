"""Scène 02 — Vue d'ensemble : ampleur du risque et évolution depuis 2019."""

from __future__ import annotations

import dash
from dash import Output, callback, html

from app import data_access as da
from app import echarts as E
from app import figures as F
from app.components.blocks import insight, scene_header, scene_layout, scene_nav
from app.components.chart_card import chart_card, chip_filtre, echart_id, graph_id
from app.components.format import fmt_number, fmt_pct
from app.components.kpi_card import kpi_card, kpi_row
from app.components.scene_utils import (
    ENTREES,
    SEUIL,
    deltas_annuels,
    fmt_ou_na,
    libelle_kpi,
    lire,
    par_annee,
    taux_masque,
)
from app.scenes import voisines
from design.tokens import tokens
from pipeline import config as C
from pipeline.indicators import base_100, letalite

dash.register_page(__name__, path="/vue-ensemble", name="Vue d'ensemble", order=2,
                   title="Vue d'ensemble · Risque routier")
NUM = 2
COLS = ["tues", "hospitalises", "legers", "victimes"]


def _national():
    s = par_annee("s02_gravite", da.TERRITOIRE_FRANCE, COLS)
    return s


def titre():
    """Titre-message généré depuis les données nationales (G3)."""
    s = _national()["tues"]
    a0, a1 = da.PREMIERE_ANNEE, da.DERNIERE_ANNEE
    ecart = (s[a1] / s[a0] - 1) * 100
    if abs(ecart) < 3:
        return ("Les tués ne baissent plus :", f"{a1} retrouve le niveau de {a0}.")
    if ecart < 0:
        return ("Les tués reculent,", f"de {fmt_pct(-ecart, 0)} depuis {a0}.")
    return ("Les tués augmentent,", f"de {fmt_pct(ecart, 0)} depuis {a0}.")


def chapeau():
    s = _national()
    a0, a1 = da.PREMIERE_ANNEE, da.DERNIERE_ANNEE
    return (f"En {a1}, {fmt_number(s['tues'][a1])} personnes sont mortes sur les routes de "
            f"métropole et {fmt_number(s['hospitalises'][a1])} ont été hospitalisées. Les "
            f"victimes reculent de {fmt_pct((1 - s['victimes'][a1] / s['victimes'][a0]) * 100, 0)}"
            f" depuis {a0}, pas les tués.")


def et_alors():
    s = _national()
    a0, a1 = da.PREMIERE_ANNEE, da.DERNIERE_ANNEE
    let0, let1 = letalite(s["tues"][a0], s["victimes"][a0]), letalite(s["tues"][a1],
                                                                       s["victimes"][a1])
    return (f"Moins de victimes mais autant de morts : la létalité passe de "
            f"{fmt_number(let0, 1)} en {da.PREMIERE_ANNEE} à {fmt_number(let1, 1)} en "
            f"{da.DERNIERE_ANNEE} tués pour 100 victimes. Pour un "
            "assureur, la gravité moyenne d'un sinistre corporel augmente : la fréquence seule ne "
            "suffit plus à suivre la sinistralité.")


def layout(**_):
    debut, accent = titre()
    return scene_layout(
        scene_header(NUM, "Vue d'ensemble", debut, accent, chapeau()),
        html.Div(id="s02-kpis"),
        html.Div(className="grille-2", children=[
            chart_card("s02-base100", "Depuis 2019, les tués décrochent des blessés",
                       "Indice base 100 en 2019 : tués, blessés hospitalisés, blessés légers.",
                       da.SOURCE_BAAC, "valeur de l'année / valeur 2019 × 100",
                       hauteur=340),
            chart_card("s02-letalite", "La létalité, année par année",
                       "Tués pour 100 victimes ; sous l'axe, la variation d'une année sur "
                       "l'autre.", da.SOURCE_BAAC, "létalité = tués / victimes × 100 ; années "
                       "sous 30 victimes masquées", hauteur=340),
        ]),
        html.Div(className="grille-2-1", children=[
            chart_card("s02-barres", "Tués par an",
                       "Personnes décédées dans les 30 jours suivant l'accident.",
                       da.SOURCE_BAAC, "usagers de gravité « tué » (décès à 30 jours)",
                       hauteur=340),
            chart_card("s02-donut", "Répartition des victimes par gravité",
                       "Répartition des victimes par gravité.", da.SOURCE_BAAC,
                       "tués, blessés hospitalisés (> 24 h), blessés légers", hauteur=340),
        ]),
        html.Div(className="grille-2-1", children=[
            chart_card("s02-rose", "Saisonnalité des tués",
                       "Tués par mois de l'accident, sur la période et le territoire choisis.",
                       da.SOURCE_BAAC, "usagers tués, par mois de l'accident", hauteur=380,
                       moteur="echarts"),
            chart_card("s02-jauge", "Létalité de la période",
                       "Tués pour 100 victimes ; trait : niveau de 2019.", da.SOURCE_BAAC,
                       "létalité = tués / victimes × 100", hauteur=300, moteur="echarts"),
        ]),
        chart_card("s02-entonnoir", "De l'accident au décès",
                   "Accidents corporels, victimes, victimes tuées ou hospitalisées, tués.",
                   da.SOURCE_BAAC, "chaque étape est un sous-ensemble de la précédente "
                   "(échelle logarithmique)", hauteur=280),
        insight(et_alors()),
        scene_nav(*voisines(NUM)),
    )


@callback(Output("s02-kpis", "children"), *ENTREES)
def kpis(filtres, scheme):
    periode, dep, _ = lire(filtres, scheme)
    ans = da.annees(periode)
    s = par_annee("s02_gravite", dep, COLS)
    g = da.filtre_table("s02_gravite", periode, dep)
    pop = da.population(periode, dep)
    pop_an = da.population_par_annee(dep)
    tues, hosp, vict = (float(s.loc[ans, c].sum()) for c in ("tues", "hospitalises", "victimes"))

    def leader_type(col, libelle):
        par = g.groupby("type_usager", observed=True)[col].sum()
        if par.sum() < SEUIL:
            return None
        top = par.idxmax()
        return ("tabler:user", [f"{top} en tête : ", html.B(fmt_pct(par[top] / par.sum() * 100,
                                                                     0)), f" des {libelle}"])

    # Létalité par catégorie de route (effectif suffisant)
    lr = g.groupby("catr_groupe", observed=True)[["tues", "victimes"]].sum()
    lr = lr[(lr["victimes"] >= SEUIL) & (lr.index != "Autre")]
    leader_route = None
    if len(lr):
        lr["let"] = letalite(lr["tues"], lr["victimes"])
        top = lr["let"].idxmax()
        leader_route = ("tabler:road", [f"Plus létale : {top} ", html.B(fmt_number(
            lr.loc[top, "let"], 1))])

    # Victimes pour 100 000 hab. : série et leader
    serie_taux = (s["victimes"] / pop_an * 100_000).where(s["victimes"] >= SEUIL)
    taux = taux_masque(vict, pop, vict, 100_000)
    terr = da.table("ind_territoires")
    lib_p = da.LIBELLE_PERIODE_CUMUL if periode == da.PERIODE_CUMUL else periode
    tp = terr[terr["periode"] == lib_p].dropna(subset=["taux_victimes_100k"])
    if dep == da.TERRITOIRE_FRANCE and len(tp):
        top = tp.loc[tp["taux_victimes_100k"].idxmax()]
        leader_taux = ("tabler:map-pin", [f"{top['nom_dep']} ", html.B(fmt_number(
            top["taux_victimes_100k"], 0))])
    elif len(tp) and dep in set(tp["dep"]):
        rang = int(tp["taux_victimes_100k"].rank(ascending=False)[tp["dep"] == dep].iloc[0])
        leader_taux = ("tabler:map-pin", ["Rang ", html.B(f"{rang}"), f" sur {len(tp)}"])
    else:
        leader_taux = None

    serie_let = letalite(s["tues"], s["victimes"]).where(s["victimes"] >= SEUIL)
    let = taux_masque(tues, vict, vict, 100)  # létalité : tués / victimes × 100

    source = f"Source : {da.SOURCE_BAAC} · {da.libelle_territoire(dep)}."
    return kpi_row([
        kpi_card("s02-k1", libelle_kpi("Tués", periode), "tabler:cross", fmt_number(tues),
                 vedette=True,
                 compte=int(tues), deltas=deltas_annuels(s["tues"], periode),
                 leader=leader_type("tues", "tués"), spark=s["tues"].tolist(),
                 lire="Personnes décédées dans les 30 jours qui suivent l'accident.",
                 assureur="Le décès est l'issue la plus grave d'un sinistre corporel.",
                 source=source),
        kpi_card("s02-k2", libelle_kpi("Hospitalisés", periode), "tabler:building-hospital",
                 fmt_number(hosp), compte=int(hosp),
                 deltas=deltas_annuels(s["hospitalises"], periode),
                 leader=leader_type("hospitalises", "hospitalisés"),
                 spark=s["hospitalises"].tolist(),
                 lire="Victimes hospitalisées plus de 24 heures (indicateur non labellisé "
                      "depuis 2019).",
                 assureur="Les blessures graves sont celles qui engagent les indemnisations les "
                          "plus longues.",
                 source=source),
        kpi_card("s02-k3", libelle_kpi("Létalité", periode), "tabler:percentage",
                 fmt_ou_na(let, 1), deltas=deltas_annuels(serie_let, periode, points=True)
                 if let is not None else [], leader=leader_route,
                 spark=[v for v in serie_let.tolist()],
                 lire="Nombre de tués pour 100 victimes : la gravité moyenne d'un accident.",
                 assureur="Une létalité qui monte alourdit le coût moyen par sinistre corporel.",
                 source=source, indisponible=let is None),
        kpi_card("s02-k4", "Victimes / 100 000 hab.", "tabler:users",
                 fmt_ou_na(taux, 1), deltas=deltas_annuels(serie_taux, periode)
                 if taux is not None else [], leader=leader_taux,
                 spark=serie_taux.tolist(),
                 lire="Victimes rapportées aux habitants du département de l'accident.",
                 assureur="Fréquence par habitant, gonflée par les non-résidents en zone "
                          "touristique.",
                 source=f"Source : {da.SOURCE_BAAC} ; {da.SOURCE_INSEE}.",
                 indisponible=taux is None),
    ])


def titre_base100(series: dict) -> str:
    """Titre de la courbe calculé sur les indices de la dernière année (G3)."""
    if "Tués" not in series or len(series) < 2:
        return "Évolution des victimes depuis 2019"
    tues = series["Tués"]
    autres = [v[-1] for k, v in series.items() if k != "Tués"]
    ecart = tues[-1] - max(autres)
    if ecart > 3:
        return "Depuis 2019, les tués décrochent des blessés"
    if tues[-1] < min(autres) - 3:
        return "Les tués reculent plus vite que les blessés"
    return "Tués et blessés évoluent au même rythme"


@callback(Output(graph_id("s02-base100"), "figure"), Output(graph_id("s02-barres"), "figure"),
          Output("s02-base100-titre", "children"), *ENTREES)
def graphes(filtres, scheme):
    _, dep, scheme = lire(filtres, scheme)
    s = par_annee("s02_gravite", dep, COLS)
    series = {}
    for nom, col in (("Tués", "tues"), ("Hospitalisés", "hospitalises"), ("Légers", "legers")):
        if s[col][da.PREMIERE_ANNEE] >= SEUIL:
            series[nom] = [round(v, 1) for v in base_100(s[col], s[col][da.PREMIERE_ANNEE])]
    fig1 = F.lignes_base100(C.ANNEES, series, "Tués", scheme)
    fig2 = F.barres_annuelles(C.ANNEES, s["tues"].astype(int).tolist(), scheme)
    return fig1, fig2, titre_base100(series)


@callback(Output("s02-base100-puces", "children"), Output("s02-barres-puces", "children"),
          *ENTREES)
def puces(filtres, scheme):
    _, dep, _ = lire(filtres, scheme)
    p = [chip_filtre(x) for x in da.puces_filtres(None, dep, toutes_annees=True)]
    return p, p



@callback(Output(graph_id("s02-letalite"), "figure"), Output("s02-letalite-puces", "children"),
          Output(graph_id("s02-donut"), "figure"), Output("s02-donut-puces", "children"),
          Output("s02-donut-titre", "children"), *ENTREES)
def evolution_et_repartition(filtres, scheme):
    periode, dep, scheme = lire(filtres, scheme)
    s = par_annee("s02_gravite", dep, COLS)
    let = letalite(s["tues"], s["victimes"]).where(s["victimes"] >= SEUIL)
    if let.notna().sum() < 2:
        fig_l = F.message_figure("Moins de 30 victimes par an : létalité non affichée", scheme)
    else:
        fig_l = F.courbe_annotee(C.ANNEES, let.tolist(), scheme, unite="tués / 100 victimes",
                                 points=True)
    ans = da.annees(periode)
    tot = s.loc[ans]
    vals = [float(tot["tues"].sum()), float(tot["hospitalises"].sum()),
            float(tot["legers"].sum())]
    tk = tokens(scheme)
    if sum(vals) < SEUIL:
        fig_d = F.message_figure("Moins de 30 victimes sur ce périmètre", scheme)
        titre_d = "Répartition des victimes par gravité"
    else:
        part_graves = (vals[0] + vals[1]) / sum(vals) * 100
        fig_d = F.donut(["Tués", "Blessés hospitalisés", "Blessés légers"], vals,
                        [tk["grav-tue"], tk["grav-hospi"], tk["grav-leger"]],
                        fmt_number(sum(vals)), "victimes", scheme)
        titre_d = (f"{fmt_pct(part_graves, 0)} des victimes sont tuées ou hospitalisées")
    p_toutes = [chip_filtre(x) for x in da.puces_filtres(None, dep, toutes_annees=True)]
    p_periode = [chip_filtre(x) for x in da.puces_filtres(periode, dep)]
    return fig_l, p_toutes, fig_d, p_periode, titre_d


MOIS_NOMS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
             "septembre", "octobre", "novembre", "décembre"]


@callback(Output(echart_id("s02-rose"), "data"), Output("s02-rose-puces", "children"),
          Output("s02-rose-titre", "children"), Output(echart_id("s02-jauge"), "data"),
          Output("s02-jauge-puces", "children"), *ENTREES)
def saisonnalite_et_jauge(filtres, scheme):
    periode, dep, scheme = lire(filtres, scheme)
    puces = [chip_filtre(x) for x in da.puces_filtres(periode, dep)]
    m = da.filtre_table("s02_mois", periode, dep).groupby("mois")["tues"].sum().reindex(
        range(1, 13), fill_value=0)
    if m.sum() < SEUIL or m.min() == 0:
        fig_r = (E.message("Moins de 30 tués sur ce périmètre", scheme) if m.sum() < SEUIL
                 else E.rose_mois(m.astype(int).tolist(), scheme))
        titre_r = "Saisonnalité des tués"
    else:
        fig_r = E.rose_mois(m.astype(int).tolist(), scheme)
        mmax, mmin = int(m.idxmax()), int(m.idxmin())
        if m.min() >= SEUIL:
            titre_r = (f"{MOIS_NOMS[mmax - 1].capitalize()} compte "
                       f"{fmt_number(m.max() / m.min(), 1)} fois plus de tués que "
                       f"{MOIS_NOMS[mmin - 1]}")
        else:
            titre_r = f"Le mois le plus meurtrier : {MOIS_NOMS[mmax - 1]}"
    s = par_annee("s02_gravite", dep, COLS)
    ans = da.annees(periode)
    vict = s.loc[ans, "victimes"].sum()
    if vict < SEUIL:
        fig_j = E.message("Moins de 30 victimes sur ce périmètre", scheme)
    else:
        let = letalite(s.loc[ans, "tues"].sum(), vict)
        ref = None
        a0 = da.PREMIERE_ANNEE
        if periode != da.PERIODE_CUMUL and int(periode) != a0 and s["victimes"][a0] >= SEUIL:
            ref = letalite(s["tues"][a0], s["victimes"][a0])
        fig_j = E.jauge(let, ref, 0, max(10, let * 1.4), scheme, lib_ref=f"{a0}",
                        decimals=1)
    return fig_r, puces, titre_r, fig_j, puces


@callback(Output(graph_id("s02-entonnoir"), "figure"), Output("s02-entonnoir-puces", "children"),
          Output("s02-entonnoir-titre", "children"), *ENTREES)
def entonnoir_gravite(filtres, scheme):
    periode, dep, scheme = lire(filtres, scheme)
    acc = float(da.filtre_table("s02_accidents", periode, dep)["accidents"].sum())
    g = da.filtre_table("s02_gravite", periode, dep)[["victimes", "tues", "hospitalises"]].sum()
    puces = [chip_filtre(x) for x in da.puces_filtres(periode, dep)]
    if g["victimes"] < SEUIL:
        return (F.message_figure("Moins de 30 victimes sur ce périmètre", scheme), puces,
                "De l'accident au décès")
    etapes = ["Accidents corporels", "Victimes", "Tués ou hospitalisés", "Tués"]
    valeurs = [acc, float(g["victimes"]), float(g["tues"] + g["hospitalises"]), float(g["tues"])]
    titre = "De l'accident au décès"
    if g["tues"]:
        titre = (f"{fmt_number(g['victimes'] / acc, 2)} victimes par accident ; "
                 f"une victime sur {fmt_number(g['victimes'] / g['tues'], 0)} est tuée")
    return F.entonnoir(etapes, valeurs, scheme), puces, titre
