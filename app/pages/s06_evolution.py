"""Scène 06 — Ce qui change : qu'est-ce qui dérive depuis 2019 ?"""

from __future__ import annotations

from functools import lru_cache

import dash
import pandas as pd
from dash import Output, callback, html

from app import data_access as da
from app import figures as F
from app.components.blocks import insight, scene_header, scene_layout, scene_nav
from app.components.chart_card import chart_card, chip_filtre, graph_id
from app.components.format import delta, fmt_number, fmt_pct
from app.components.kpi_card import kpi_card, kpi_row
from app.components.scene_utils import ENTREES, SEUIL, deltas_annuels, fmt_ou_na, lire, par_annee
from app.scenes import voisines
from design.tokens import tokens
from pipeline import config as C
from pipeline.indicators import base_100

dash.register_page(__name__, path="/evolution", name="Ce qui change", order=6,
                   title="Ce qui change · Risque routier")
NUM = 6
SEUIL_PARETO = 80
A0 = da.PREMIERE_ANNEE


def victimes_par_type(dep) -> pd.DataFrame:
    g = da.filtre_table("s02_gravite", dep=dep, toutes_annees=True)
    return g.pivot_table(index="annee", columns="type_usager", values="victimes",
                         aggfunc="sum", observed=True).reindex(C.ANNEES).fillna(0)


def evolution(v: pd.Series, a1: int):
    """Évolution en % de 2019 à a1, masquée si un des deux effectifs est sous le seuil."""
    if v.get(A0, 0) < SEUIL or v.get(a1, 0) < SEUIL:
        return None
    return (v[a1] / v[A0] - 1) * 100


def poids_pareto():
    """Coût socio-économique si les valeurs tutélaires sont sourcées (G8), sinon tués + hosp."""
    vt = (da.references() or {}).get("valeurs_tutelaires_eur") or {}
    if all(vt.get(k) is not None for k in ("tue", "blesse_hospitalise", "blesse_leger")) and \
            vt.get("source"):
        return vt
    return None


NOMS = {"EDP": "en trottinette ou EDP", "Vélo": "à vélo", "Piéton": "piétonnes",
        "2RM": "en deux-roues motorisé", "Voiture": "en voiture", "Utilitaire": "en utilitaire",
        "Poids lourd": "en poids lourd", "Bus, car, tram": "en transport collectif",
        "Autre": "des autres véhicules"}


def plus_forte_hausse(v: pd.DataFrame, a1: int):
    evols = {c: evolution(v[c], a1) for c in v.columns if c != "Autre"}
    evols = {c: e for c, e in evols.items() if e is not None}
    return max(evols.items(), key=lambda x: x[1]) if evols else (None, None)


def titre():
    v = victimes_par_type(da.TERRITOIRE_FRANCE)
    a1 = da.DERNIERE_ANNEE
    top, ev = plus_forte_hausse(v, a1)
    if top is None:
        return ("Les victimes par mode de déplacement", f"depuis {A0}.")
    facteur = v[top][a1] / v[top][A0]
    if facteur >= 2:
        return (f"Les victimes {NOMS[top]}", f"ont été multipliées par {fmt_number(facteur, 0)} "
                f"depuis {A0}.")
    return (f"Les victimes {NOMS[top]}", f"progressent le plus : {fmt_pct(ev, 0, signe=True)}.")


def chapeau():
    v = victimes_par_type(da.TERRITOIRE_FRANCE)
    a1 = da.DERNIERE_ANNEE
    return (f"De {A0} à {a1}, les victimes en trottinette et autres engins (EDP) passent de "
            f"{fmt_number(v['EDP'][A0])} à {fmt_number(v['EDP'][a1])}, celles à vélo varient de "
            f"{fmt_pct(evolution(v['Vélo'], a1), 0, signe=True)}, celles en voiture de "
            f"{fmt_pct(evolution(v['Voiture'], a1), 0, signe=True)}.")


def _pareto(periode, dep):
    g = da.filtre_table("s02_gravite", periode, dep).groupby(
        ["type_usager", "agg_lib"], observed=True)[["tues", "hospitalises", "legers"]].sum()
    vt = poids_pareto()
    if vt:
        g["poids"] = (g["tues"] * vt["tue"] + g["hospitalises"] * vt["blesse_hospitalise"]
                      + g["legers"] * vt["blesse_leger"])
    else:
        g["poids"] = g["tues"] + g["hospitalises"]
    g = g[g["poids"] > 0].sort_values("poids", ascending=False)
    g["part"] = g["poids"] / g["poids"].sum() * 100
    g["cumul"] = g["part"].cumsum()
    g["lib"] = [f"{t} · {'hors agglo.' if a.startswith('Hors') else 'en agglo.'}"
                for t, a in g.index]
    total = (g["tues"] + g["hospitalises"]).sum()
    # Queue regroupée : segments au-delà de 95 % de cumul -> « Autres segments »
    garde = g["cumul"].shift(fill_value=0) < 95
    if (~garde).sum() > 1:
        reste = g[~garde]
        autres = pd.DataFrame({"part": [reste["part"].sum()], "cumul": [100.0],
                               "lib": [f"Autres segments ({len(reste)})"]})
        g = pd.concat([g[garde][["part", "cumul", "lib"]], autres], ignore_index=True)
    return g, total


def et_alors():
    g, _ = _pareto(da.PERIODE_CUMUL, da.TERRITOIRE_FRANCE)
    n = int((g["cumul"] < SEUIL_PARETO).sum()) + 1
    top = g.iloc[0]["lib"]
    nb = len(da.table("s02_gravite").groupby(["type_usager", "agg_lib"], observed=True))
    part = fmt_pct(g["cumul"].iloc[n - 1], 0)
    return (f"Sur {da.LIBELLE_PERIODE_CUMUL}, {n} segments sur {nb} concentrent {part} de la "
            f"gravité, emmenés par « {top} » : c'est là que tarification fine et prévention "
            "rapportent le plus. Les engins de déplacement personnel, encore marginaux, sont à "
            "surveiller.")


def layout(**_):
    debut, accent = titre()
    critere = ("coût socio-économique" if poids_pareto() else "tués + blessés hospitalisés")
    return scene_layout(
        scene_header(NUM, "Ce qui change", debut, accent, chapeau()),
        html.Div(id="s06-kpis"),
        chart_card("s06-multiples", "Victimes par mode de déplacement, base 100 en 2019",
                   f"Victimes par type d'usager, indice base 100 en {A0}, même échelle.",
                   da.SOURCE_BAAC, f"victimes de l'année / victimes {A0} × 100 ; types sous 30 "
                   f"victimes en {A0} non affichés", hauteur=520),
        html.Div(className="grille-2", children=[
            chart_card("s06-pente", f"Les victimes par mode, de {A0} à {da.DERNIERE_ANNEE}",
                       "Une ligne par mode ; échelle logarithmique pour comparer les pentes.",
                       da.SOURCE_BAAC, "victimes de l'année ; modes sous 30 victimes exclus",
                       hauteur=420),
            chart_card("s06-modes", "Comment se répartissent les tués, année après année",
                       "Part de chaque mode de déplacement parmi les tués, par année.",
                       da.SOURCE_BAAC, "tués d'un mode / total des tués de l'année ; années "
                       "sous 30 tués non affichées", hauteur=420),
        ]),
        chart_card("s06-pareto", f"Quelques segments concentrent la gravité ({critere})",
                   "Segments type d'usager × agglomération, triés par poids décroissant ; ligne "
                   "= part cumulée.", da.SOURCE_BAAC,
                   (f"poids = {critere}" + ("" if poids_pareto() else
                                             " (valeurs tutélaires de coût : À renseigner dans "
                                             "config/references.yaml)")), hauteur=380),
        insight(et_alors()),
        scene_nav(*voisines(NUM)),
    )


@callback(Output("s06-kpis", "children"), *ENTREES)
def kpis(filtres, scheme):
    periode, dep, _ = lire(filtres, scheme)
    a1 = da.annee_ref(periode)
    s = par_annee("s02_gravite", dep, ["tues"])["tues"]
    v = victimes_par_type(dep)
    src = f"Source : {da.SOURCE_BAAC} · {da.libelle_territoire(dep)}."

    def carte_evol(kid, label, icon, serie, lire_txt, assureur, plus_est_mauvais=True,
                   vedette=False):
        vedette = vedette or kid == "s06-k1"
        ev = evolution(serie, a1) if a1 > A0 else None
        if callable(assureur):
            assureur = assureur(ev)
        if ev is None:
            return kpi_card(kid, label, icon, "—", lire=lire_txt, assureur=assureur,
                            source=src, indisponible=True, vedette=vedette)
        return kpi_card(
            kid, label, icon, fmt_pct(ev, 1, signe=True),
            deltas=[delta(serie[a1], serie[a1 - 1], str(a1 - 1), plus_est_mauvais)]
            if a1 > A0 else [],
            leader=("tabler:arrow-right", [f"{fmt_number(serie[A0])} en {A0} → ",
                                           html.B(fmt_number(serie[a1])), f" en {a1}"]),
            spark=base_100(serie, serie[A0]).tolist(), lire=lire_txt, assureur=assureur,
            source=src, vedette=vedette)

    s2rm = []
    for a in C.ANNEES:
        ta = da.filtre_table("s02_gravite", str(a), dep).groupby(
            "type_usager", observed=True)["tues"].sum()
        s2rm.append(ta.get("2RM", 0) / ta.sum() * 100 if ta.sum() >= SEUIL else None)
    s2rm = pd.Series(s2rm, index=C.ANNEES, dtype=float)
    part2rm = s2rm[a1]
    return kpi_row([
        carte_evol("s06-k1", f"Tués {A0} → {a1}", "tabler:cross", s,
                   "Évolution du nombre de tués entre 2019 et l'année choisie.",
                   lambda ev: ("Pas de baisse tendancielle de la mortalité à intégrer dans "
                               "les hypothèses." if ev is not None and abs(ev) < 3 else
                               "Une tendance à confronter à l'évolution de la charge des "
                               "sinistres corporels.")),
        carte_evol("s06-k2", f"Victimes EDP {A0} → {a1}", "tabler:scooter", v.get("EDP"),
                   "Évolution des victimes en trottinette ou autre engin de déplacement "
                   "personnel.", "Un mode de déplacement à suivre pour les garanties de "
                   "responsabilité civile."),
        carte_evol("s06-k3", f"Victimes vélo {A0} → {a1}", "tabler:bike", v.get("Vélo"),
                   "Évolution des victimes à vélo (y compris à assistance électrique).",
                   "Cycliste blessé : indemnisé par l'assureur du véhicule (responsabilité "
                   "civile)."),
        kpi_card("s06-k4", f"Part des 2RM (tués) · {a1}", "tabler:motorbike",
                 fmt_ou_na(None if pd.isna(part2rm) else part2rm, 1, pct=True),
                 deltas=deltas_annuels(s2rm, str(a1), None, points=True)
                 if not pd.isna(part2rm) else [],
                 spark=s2rm.tolist(),
                 lire="Part des usagers de deux-roues motorisés parmi les tués.",
                 assureur="À rapprocher de la part des 2RM dans le trafic : "
                          f"{(da.references() or {}).get('part_trafic_2rm_pct') or 'À renseigner'}"
                          " (voir Méthode).",
                 source=src, indisponible=pd.isna(part2rm)),
    ])


@callback(Output(graph_id("s06-multiples"), "figure"), Output("s06-multiples-puces", "children"),
          Output(graph_id("s06-pareto"), "figure"), Output("s06-pareto-puces", "children"),
          Output("s06-multiples-titre", "children"), *ENTREES)
def graphes(filtres, scheme):
    periode, dep, scheme = lire(filtres, scheme)
    fig_m, titre_m = petits_multiples(dep, scheme)
    g, total = _pareto(periode, dep)
    if total < SEUIL or g.empty:
        fig_p = F.message_figure("Moins de 30 victimes graves sur ce périmètre", scheme)
    else:
        fig_p = F.pareto(g["lib"].tolist(), g["part"].round(2).tolist(),
                         g["cumul"].round(2).tolist(), SEUIL_PARETO, scheme)
    return (fig_m, [chip_filtre(x) for x in da.puces_filtres(None, dep, toutes_annees=True)],
            fig_p, [chip_filtre(x) for x in da.puces_filtres(periode, dep)], titre_m)


@lru_cache(maxsize=256)
def petits_multiples(dep: str, scheme: str):
    """Ne dépend que du territoire et du thème : mis en cache (figure lourde à construire)."""
    v = victimes_par_type(dep)
    series = {c: [round(x, 1) for x in base_100(v[c], v[c][A0])]
              for c in C.TYPE_USAGER_ORDRE if c in v.columns and v[c][A0] >= SEUIL}
    titre_m = "Victimes par mode de déplacement, base 100 en 2019"
    if not series:
        return F.message_figure("Effectifs trop faibles par type d'usager", scheme), titre_m
    alerte = max(series, key=lambda c: series[c][-1])
    if series[alerte][-1] > 110:
        titre_m = (f"Les victimes {NOMS[alerte]} progressent le plus "
                   f"(indice {fmt_number(series[alerte][-1])})")
    return F.petits_multiples(C.ANNEES, series, alerte, scheme), titre_m


GROUPES_MODES = {"Voiture": ["Voiture"], "2RM": ["2RM"], "Piéton": ["Piéton"], "Vélo": ["Vélo"],
                 "EDP": ["EDP"], "Autres": ["Utilitaire", "Poids lourd", "Bus, car, tram",
                                            "Autre"]}


@callback(Output(graph_id("s06-modes"), "figure"), Output("s06-modes-puces", "children"),
          Output("s06-modes-titre", "children"), *ENTREES)
def repartition_modes(filtres, scheme):
    _, dep, scheme = lire(filtres, scheme)
    g = da.filtre_table("s02_gravite", dep=dep, toutes_annees=True).pivot_table(
        index="annee", columns="type_usager", values="tues", aggfunc="sum",
        observed=True).reindex(C.ANNEES).fillna(0)
    tot = g.sum(axis=1)
    ok = tot >= SEUIL
    puces = [chip_filtre(x) for x in da.puces_filtres(None, dep, toutes_annees=True)]
    if ok.sum() < 2:
        return (F.message_figure("Moins de 30 tués par an sur ce périmètre", scheme), puces,
                "Répartition des tués par mode")
    tk = tokens(scheme)
    parts, couleurs = {}, {}
    for i, (nom, types) in enumerate(GROUPES_MODES.items(), start=1):
        cols = [c for c in types if c in g.columns]
        parts[nom] = (g[cols].sum(axis=1) / tot * 100)[ok].round(1).tolist()
        couleurs[nom] = tk[f"cat-{i}"]
    annees = [int(a) for a in tot[ok].index]
    fig = F.barres_100(annees, parts, couleurs, scheme)
    premier = max(parts, key=lambda k: parts[k][-1])
    titre_m = (f"{premier} : {fmt_pct(parts[premier][-1], 0)} des tués en {annees[-1]}, "
               f"contre {fmt_pct(parts[premier][0], 0)} en {annees[0]}")
    return fig, puces, titre_m


@callback(Output(graph_id("s06-pente"), "figure"), Output("s06-pente-puces", "children"),
          Output("s06-pente-titre", "children"), *ENTREES)
def graphique_pente(filtres, scheme):
    _, dep, scheme = lire(filtres, scheme)
    v = victimes_par_type(dep)
    a1 = da.DERNIERE_ANNEE
    modes = [c for c in C.TYPE_USAGER_ORDRE if c in v.columns and c != "Autre"
             and v[c][A0] >= SEUIL and v[c][a1] >= SEUIL]
    puces = [chip_filtre(x) for x in da.puces_filtres(None, dep, toutes_annees=True)]
    if len(modes) < 2:
        return (F.message_figure("Effectifs trop faibles par mode", scheme), puces,
                f"Les victimes par mode, de {A0} à {a1}")
    top, ev = plus_forte_hausse(v[modes], a1)
    fig = F.pente(modes, [float(v[c][A0]) for c in modes], [float(v[c][a1]) for c in modes],
                  (A0, a1), scheme, alerte=top)
    return fig, puces, f"{top} : {fmt_pct(ev, 0, signe=True)} de victimes en {a1 - A0} ans"
