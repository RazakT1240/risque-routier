"""Scène 02 — Vue d'ensemble : ampleur du risque et évolution depuis 2019."""

from __future__ import annotations

import dash
from dash import Output, callback, html

from app import data_access as da
from app import figures as F
from app.components.blocks import insight, scene_header, scene_layout, scene_nav
from app.components.chart_card import chart_card, chip_filtre, graph_id
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
            f"{fmt_number(let0, 1)} à {fmt_number(let1, 1)} tués pour 100 victimes. Pour un "
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
            chart_card("s02-barres", "Tués par an",
                       "Personnes décédées dans les 30 jours suivant l'accident.",
                       da.SOURCE_BAAC, "usagers de gravité « tué » (décès à 30 jours)",
                       hauteur=340),
        ]),
        insight(et_alors()),
        scene_nav(*voisines(NUM)),
    )


@callback(Output("s02-kpis", "children"), *ENTREES)
def kpis(filtres, scheme):
    periode, dep, _ = lire(filtres, scheme)
    ans = da.annees(periode)
    s = par_annee("s02_gravite", dep, COLS)
    g = da.filtrer(da.table("s02_gravite"), periode, dep)
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
                 lire="Victimes rapportées à la population du département de l'accident : les "
                      "départements touristiques ou de transit sont gonflés par les non-résidents.",
                 assureur="La fréquence corporelle par habitant, comparable entre territoires.",
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

