"""Scène 06 — Ce qui change : qu'est-ce qui dérive depuis 2019 ?"""

from __future__ import annotations

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
from pipeline import config as C
from pipeline.indicators import base_100

dash.register_page(__name__, path="/evolution", name="Ce qui change", order=6,
                   title="Ce qui change · Risque routier")
NUM = 6
SEUIL_PARETO = 80
A0 = da.PREMIERE_ANNEE


def victimes_par_type(dep) -> pd.DataFrame:
    g = da.filtrer(da.table("s02_gravite"), dep=dep, toutes_annees=True)
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


def titre():
    v = victimes_par_type(da.TERRITOIRE_FRANCE)
    a1 = da.DERNIERE_ANNEE
    edp, velo, voit = (evolution(v[c], a1) for c in ("EDP", "Vélo", "Voiture"))
    if edp and velo and voit is not None and edp > 0 and velo > 0 and voit < 0:
        return ("Trottinettes et vélos progressent,", "la voiture recule.")
    top = max(((c, evolution(v[c], a1)) for c in v.columns if evolution(v[c], a1) is not None),
              key=lambda x: x[1])
    return (f"Les victimes {top[0].lower()} progressent", "plus vite que les autres.")


def chapeau():
    v = victimes_par_type(da.TERRITOIRE_FRANCE)
    a1 = da.DERNIERE_ANNEE
    return (f"De {A0} à {a1}, les victimes en trottinette et autres engins (EDP) passent de "
            f"{fmt_number(v['EDP'][A0])} à {fmt_number(v['EDP'][a1])}, celles à vélo varient de "
            f"{fmt_pct(evolution(v['Vélo'], a1), 0, signe=True)}, celles en voiture de "
            f"{fmt_pct(evolution(v['Voiture'], a1), 0, signe=True)}.")


def _pareto(periode, dep):
    g = da.filtrer(da.table("s02_gravite"), periode, dep).groupby(
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
    return (f"{n} segments sur {nb} concentrent {fmt_pct(g['cumul'].iloc[n - 1], 0)} de la "
            f"gravité, emmenés par « {top} » : c'est là que tarification fine et prévention "
            "rapportent le plus. Les engins de déplacement personnel, encore marginaux, sont à "
            "surveiller.")


def layout(**_):
    debut, accent = titre()
    critere = ("coût socio-économique" if poids_pareto() else "tués + blessés hospitalisés")
    return scene_layout(
        scene_header(NUM, "Ce qui change", debut, accent, chapeau()),
        html.Div(id="s06-kpis"),
        chart_card("s06-multiples", "Chaque mode de déplacement suit sa propre trajectoire",
                   f"Victimes par type d'usager, indice base 100 en {A0}, même échelle.",
                   da.SOURCE_BAAC, f"victimes de l'année / victimes {A0} × 100 ; types sous 30 "
                   f"victimes en {A0} non affichés", hauteur=520),
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

    def carte_evol(kid, label, icon, serie, lire_txt, assureur, plus_est_mauvais=True):
        ev = evolution(serie, a1)
        if ev is None:
            return kpi_card(kid, label, icon, "—", lire=lire_txt, assureur=assureur,
                            source=src, indisponible=True)
        return kpi_card(
            kid, label, icon, fmt_pct(ev, 1, signe=True),
            deltas=[delta(serie[a1], serie[a1 - 1], str(a1 - 1), plus_est_mauvais)]
            if a1 > A0 else [],
            leader=("tabler:arrow-right", [f"{fmt_number(serie[A0])} en {A0} → ",
                                           html.B(fmt_number(serie[a1])), f" en {a1}"]),
            spark=base_100(serie, serie[A0]).tolist(), lire=lire_txt, assureur=assureur,
            source=src)

    s2rm = []
    for a in C.ANNEES:
        ta = da.filtrer(da.table("s02_gravite"), str(a), dep).groupby(
            "type_usager", observed=True)["tues"].sum()
        s2rm.append(ta.get("2RM", 0) / ta.sum() * 100 if ta.sum() >= SEUIL else None)
    s2rm = pd.Series(s2rm, index=C.ANNEES, dtype=float)
    part2rm = s2rm[a1]
    return kpi_row([
        carte_evol("s06-k1", f"Tués {A0} → {a1}", "tabler:cross", s,
                   "Évolution du nombre de tués entre 2019 et l'année choisie.",
                   "La sinistralité mortelle ne recule plus : pas de baisse tendancielle à "
                   "intégrer dans les tarifs."),
        carte_evol("s06-k2", f"Victimes EDP {A0} → {a1}", "tabler:scooter", v.get("EDP"),
                   "Évolution des victimes en trottinette ou autre engin de déplacement "
                   "personnel.", "Un risque émergent, mal couvert par les contrats auto "
                   "classiques."),
        carte_evol("s06-k3", f"Victimes vélo {A0} → {a1}", "tabler:bike", v.get("Vélo"),
                   "Évolution des victimes à vélo (y compris à assistance électrique).",
                   "Plus de cyclistes exposés : enjeu de responsabilité civile pour les "
                   "automobilistes assurés."),
        kpi_card("s06-k4", f"Part des 2RM (tués) · {a1}", "tabler:motorbike",
                 fmt_ou_na(None if pd.isna(part2rm) else part2rm, 1, pct=True),
                 deltas=deltas_annuels(s2rm, str(a1), None) if not pd.isna(part2rm) else [],
                 spark=s2rm.tolist(),
                 lire="Part des usagers de deux-roues motorisés parmi les tués.",
                 assureur="Un poids stable et élevé : le 2RM reste le segment le plus exposé.",
                 source=src, indisponible=pd.isna(part2rm)),
    ])


@callback(Output(graph_id("s06-multiples"), "figure"), Output("s06-multiples-puces", "children"),
          Output(graph_id("s06-pareto"), "figure"), Output("s06-pareto-puces", "children"),
          *ENTREES)
def graphes(filtres, scheme):
    periode, dep, scheme = lire(filtres, scheme)
    v = victimes_par_type(dep)
    series = {c: [round(x, 1) for x in base_100(v[c], v[c][A0])]
              for c in C.TYPE_USAGER_ORDRE if c in v.columns and v[c][A0] >= SEUIL}
    if series:
        alerte = max(series, key=lambda c: series[c][-1])
        fig_m = F.petits_multiples(C.ANNEES, series, alerte, scheme)
    else:
        fig_m = F.message_figure("Effectifs trop faibles par type d'usager", scheme)
    g, total = _pareto(periode, dep)
    if total < SEUIL or g.empty:
        fig_p = F.message_figure("Moins de 30 victimes graves sur ce périmètre", scheme)
    else:
        fig_p = F.pareto(g["lib"].tolist(), g["part"].round(2).tolist(),
                         g["cumul"].round(2).tolist(), SEUIL_PARETO, scheme)
    return (fig_m, [chip_filtre(x) for x in da.puces_filtres(None, dep, toutes_annees=True)],
            fig_p, [chip_filtre(x) for x in da.puces_filtres(periode, dep)])
