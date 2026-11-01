"""Scène 03 — Le paradoxe : les accidents et les tués ne sont pas au même endroit."""

from __future__ import annotations

import dash
from dash import Input, Output, callback, html

from app import data_access as da
from app import figures as F
from app.components.blocks import (
    bascule,
    bascule_id,
    insight,
    scene_header,
    scene_layout,
    scene_nav,
)
from app.components.chart_card import chart_card, chip_filtre, graph_id
from app.components.format import fmt_number, fmt_pct, fmt_ratio
from app.components.kpi_card import kpi_card, kpi_row
from app.components.scene_utils import ENTREES, SEUIL, deltas_annuels, fmt_ou_na, lire
from app.scenes import voisines
from design.tokens import tokens
from pipeline import config as C
from pipeline.indicators import letalite

dash.register_page(__name__, path="/paradoxe", name="Le paradoxe", order=3,
                   title="Le paradoxe · Risque routier")
NUM = 3
HORS, EN = "Hors agglomération", "En agglomération"
VUES = {"Vitesse autorisée": ("s03_vma", "vma"), "Lumière": ("s03_lum", "lum_groupe"),
        "Obstacle heurté": ("s03_obs", "obs_groupe")}
ORDRES = {"vma": sorted(C.VMA_VALIDES), "lum_groupe": C.LUM_GROUPE_ORDRE,
          "obs_groupe": C.OBS_GROUPE_ORDRE}


def _agg(periode, dep):
    acc = da.filtrer(da.table("s02_accidents"), periode, dep).groupby("agg_lib")[
        "accidents"].sum()
    usa = da.filtrer(da.table("s02_gravite"), periode, dep).groupby("agg_lib")[
        ["tues", "victimes"]].sum()
    return acc, usa


def _series_annuelles(dep):
    acc = da.filtrer(da.table("s02_accidents"), dep=dep, toutes_annees=True).pivot_table(
        index="annee", columns="agg_lib", values="accidents", aggfunc="sum").reindex(C.ANNEES)
    usa = da.filtrer(da.table("s02_gravite"), dep=dep, toutes_annees=True).pivot_table(
        index="annee", columns="agg_lib", values=["tues", "victimes"], aggfunc="sum").reindex(
        C.ANNEES)
    part_acc_en = acc[EN] / acc.sum(axis=1) * 100
    part_tues_hors = usa["tues"][HORS] / usa["tues"].sum(axis=1) * 100
    let_hors = letalite(usa["tues"][HORS], usa["victimes"][HORS]).where(
        usa["victimes"][HORS] >= SEUIL)
    let_en = letalite(usa["tues"][EN], usa["victimes"][EN]).where(usa["victimes"][EN] >= SEUIL)
    return part_acc_en, part_tues_hors, let_hors, let_hors / let_en


def _national():
    acc, usa = _agg(da.PERIODE_CUMUL, da.TERRITOIRE_FRANCE)
    return {"part_acc_en": acc[EN] / acc.sum() * 100,
            "part_tues_hors": usa.loc[HORS, "tues"] / usa["tues"].sum() * 100,
            "let_hors": letalite(usa.loc[HORS, "tues"], usa.loc[HORS, "victimes"]),
            "let_en": letalite(usa.loc[EN, "tues"], usa.loc[EN, "victimes"])}


def titre():
    n = _national()
    if n["part_acc_en"] > 50 and n["part_tues_hors"] > 50:
        return ("La ville fait les accidents,", "la campagne fait les morts.")
    if n["let_hors"] > n["let_en"]:
        return ("Hors agglomération, un accident est", "bien plus souvent mortel.")
    return ("Accidents et tués", "se concentrent au même endroit.")


def chapeau():
    n = _national()
    return (f"Sur {da.LIBELLE_PERIODE_CUMUL}, {fmt_pct(n['part_acc_en'], 0)} des accidents "
            f"corporels ont lieu en agglomération, mais {fmt_pct(n['part_tues_hors'], 0)} des "
            "tués meurent hors agglomération.")


def et_alors():
    n = _national()
    fois = fmt_number(n["let_hors"] / n["let_en"], 1)
    return (f"Hors agglomération, une victime est {fois} fois plus souvent tuée qu'en ville : "
            "c'est la sévérité, pas la fréquence, qui fait la gravité des sinistres ruraux. Un "
            "zonage fondé sur le seul nombre d'accidents la sous-estime.")


def layout(**_):
    debut, accent = titre()
    return scene_layout(
        scene_header(NUM, "Le paradoxe", debut, accent, chapeau()),
        html.Div(id="s03-kpis"),
        html.Div(className="grille-2", children=[
            chart_card("s03-miroir", "Accidents et tués par type de route",
                       "Part des accidents (à gauche) et part des tués (à droite) par type de "
                       "route.", da.SOURCE_BAAC,
                       "part de chaque catégorie de route dans le total des accidents corporels "
                       "et dans le total des tués", hauteur=360),
            chart_card("s03-letalite", "Où un accident est-il le plus souvent mortel ?",
                       "Tués pour 100 victimes, selon la vitesse autorisée, la lumière ou "
                       "l'obstacle heurté.", da.SOURCE_BAAC,
                       "létalité = tués / victimes × 100 ; catégories sous 30 victimes grisées",
                       hauteur=320, controles=bascule("s03-vue", list(VUES),
                                                      "Vitesse autorisée", "Critère")),
        ]),
        html.Div(className="grille-2-1", children=[
            chart_card("s03-matrice", "Route × lumière : où une victime est le plus souvent tuée",
                       "Tués pour 100 victimes, par type de route et conditions de lumière.",
                       da.SOURCE_BAAC, "létalité = tués / victimes × 100 ; cases sous 30 "
                       "victimes grisées", hauteur=360),
            chart_card("s03-jauge", "Les tués hors agglomération",
                       "Part des tués dont l'accident a eu lieu hors agglomération.",
                       da.SOURCE_BAAC, "tués hors agglomération / total des tués", hauteur=300),
        ]),
        chart_card("s03-annees", "Tués selon le lieu, par année",
                   "Répartition des tués entre agglomération et hors agglomération, par année.",
                   da.SOURCE_BAAC, "part des tués selon le lieu de l'accident ; années sous 30 "
                   "tués non affichées", hauteur=320),
        insight(et_alors()),
        scene_nav(*voisines(NUM)),
    )


@callback(Output("s03-kpis", "children"), *ENTREES)
def kpis(filtres, scheme):
    periode, dep, _ = lire(filtres, scheme)
    acc, usa = _agg(periode, dep)
    p_acc, p_tues, s_let, s_ratio = _series_annuelles(dep)
    tot_acc, tot_tues = acc.sum(), usa["tues"].sum()
    part_acc_en = acc.get(EN, 0) / tot_acc * 100 if tot_acc else None
    part_tues_hors = usa["tues"].get(HORS, 0) / tot_tues * 100 if tot_tues >= SEUIL else None
    vh, ve = usa["victimes"].get(HORS, 0), usa["victimes"].get(EN, 0)
    let_hors = letalite(usa["tues"][HORS], vh) if vh >= SEUIL else None
    let_en = letalite(usa["tues"][EN], ve) if ve >= SEUIL else None
    ratio = let_hors / let_en if let_hors and let_en else None

    g = da.filtrer(da.table("s02_gravite"), periode, dep)
    a = da.filtrer(da.table("s02_accidents"), periode, dep)
    route_acc = a.groupby("catr_groupe", observed=True)["accidents"].sum()
    route_tues = g.groupby("catr_groupe", observed=True)["tues"].sum()

    def leader_part(serie, quoi):
        if serie.sum() < SEUIL:
            return None
        top = serie.idxmax()
        return ("tabler:road", [f"{top} : ", html.B(fmt_pct(serie[top] / serie.sum() * 100, 0)),
                                f" des {quoi}"])

    obs = da.filtrer(da.table("s03_obs"), periode, dep).groupby("obs_groupe", observed=True)[
        ["tues", "victimes"]].sum()
    obs = obs[obs["victimes"] >= SEUIL]
    leader_obs = None
    if len(obs):
        lo = letalite(obs["tues"], obs["victimes"])
        leader_obs = ("tabler:tree", [f"{lo.idxmax()} : ", html.B(fmt_number(lo.max(), 1)),
                                      " tués / 100 victimes"])
    lum = da.filtrer(da.table("s03_lum"), periode, dep)
    lum = lum[lum["agg_lib"] == HORS].groupby("lum_groupe", observed=True)[
        ["tues", "victimes"]].sum()
    lum = lum[lum["victimes"] >= SEUIL]
    leader_lum = None
    if len(lum):
        ll = letalite(lum["tues"], lum["victimes"])
        leader_lum = ("tabler:moon", [f"{ll.idxmax()} : ", html.B(fmt_number(ll.max(), 1))])

    src = f"Source : {da.SOURCE_BAAC} · {da.libelle_territoire(dep)}."
    return kpi_row([
        kpi_card("s03-k1", "Accidents en agglomération",
                 "tabler:building-community", fmt_ou_na(part_acc_en, 1, pct=True),
                 vedette=True,
                 deltas=deltas_annuels(p_acc, periode, None, points=True), leader=leader_part(
                     route_acc, "accidents"), spark=p_acc.tolist(),
                 lire="Part des accidents corporels survenus en agglomération.",
                 assureur="La fréquence se concentre en ville : c'est là que les sinistres "
                          "sont nombreux.", source=src, indisponible=part_acc_en is None),
        kpi_card("s03-k2", "Tués hors agglomération", "tabler:trees",
                 fmt_ou_na(part_tues_hors, 1, pct=True),
                 deltas=deltas_annuels(p_tues, periode, None, points=True),
                 leader=leader_part(route_tues, "tués"), spark=p_tues.tolist(),
                 lire="Part des tués dont l'accident a eu lieu hors agglomération.",
                 assureur="La gravité se concentre hors des villes : c'est là que se joue le "
                          "coût des sinistres lourds.", source=src,
                 indisponible=part_tues_hors is None),
        kpi_card("s03-k3", "Létalité hors agglomération",
                 "tabler:alert-triangle", fmt_ou_na(let_hors, 1),
                 deltas=deltas_annuels(s_let, periode, points=True) if let_hors else [],
                 leader=leader_lum, spark=s_let.tolist(),
                 lire="Tués pour 100 victimes, pour les accidents hors agglomération.",
                 assureur="Plus elle est haute, plus un sinistre corporel rural est coûteux.",
                 source=src, indisponible=let_hors is None),
        kpi_card("s03-k4", "Létalité hors / en agglo.", "tabler:arrows-diff",
                 fmt_ratio(ratio, 1) if ratio else "—",
                 deltas=deltas_annuels(s_ratio, periode, None) if ratio else [],
                 leader=leader_obs, spark=s_ratio.tolist(),
                 lire="Combien de fois une victime hors agglomération est plus souvent tuée "
                      "qu'une victime en ville.", assureur="Mesure l'écart de sévérité entre "
                 "territoires.", source=src, indisponible=ratio is None),
    ])


@callback(Output(graph_id("s03-miroir"), "figure"), Output("s03-miroir-puces", "children"),
          Output("s03-miroir-titre", "children"), *ENTREES)
def miroir(filtres, scheme):
    periode, dep, scheme = lire(filtres, scheme)
    a = da.filtrer(da.table("s02_accidents"), periode, dep).groupby(
        "catr_groupe", observed=True)["accidents"].sum().reindex(C.CATR_GROUPE_ORDRE, fill_value=0)
    t = da.filtrer(da.table("s02_gravite"), periode, dep).groupby(
        "catr_groupe", observed=True)["tues"].sum().reindex(C.CATR_GROUPE_ORDRE, fill_value=0)
    puces = [chip_filtre(x) for x in da.puces_filtres(periode, dep)]
    if t.sum() < SEUIL:
        return (F.message_figure("Moins de 30 tués sur ce périmètre : répartition non affichée",
                                 scheme), puces, "Accidents et tués par type de route")
    pa, pt = a / a.sum() * 100, t / t.sum() * 100
    alerte = (pt - pa).idxmax()
    noms = {"Départementale": "Les départementales", "Nationale": "Les nationales",
            "Autoroute": "Les autoroutes", "Communale": "Les voies communales",
            "Métropole urbaine": "Les routes de métropole", "Autre": "Les autres voies"}
    titre_g = (f"{noms[alerte]} font plus de morts que d'accidents"
               if pt[alerte] - pa[alerte] >= 5 else "Accidents et tués par type de route")
    return F.barres_miroir(list(pa.index), pa.round(1).tolist(), pt.round(1).tolist(), alerte,
                           "Accidents", "Tués", scheme), puces, titre_g


@callback(Output(graph_id("s03-letalite"), "figure"), Output("s03-letalite-puces", "children"),
          Input(bascule_id("s03-vue"), "value"), *ENTREES)
def letalite_par(vue, filtres, scheme):
    periode, dep, scheme = lire(filtres, scheme)
    nom, col = VUES.get(vue or "Vitesse autorisée")
    d = da.filtrer(da.table(nom), periode, dep).groupby(col, observed=True)[
        ["tues", "victimes"]].sum()
    d = d.reindex([c for c in ORDRES[col] if c in d.index])
    if col == "vma":
        d = d[d["victimes"] > 0]
    tot = da.filtrer(da.table("s02_gravite"), periode, dep)[["tues", "victimes"]].sum()
    moy = letalite(tot["tues"], tot["victimes"]) if tot["victimes"] >= SEUIL else None
    masques = [c for c in d.index if d.loc[c, "victimes"] < SEUIL]
    vals = letalite(d["tues"], d["victimes"]).fillna(0)
    etiquettes = [str(c) for c in d.index]
    masques_lib = [etiquettes[list(d.index).index(c)] for c in masques]
    puces = [chip_filtre(x) for x in da.puces_filtres(periode, dep)]
    if len(masques) == len(d):
        return F.message_figure("Moins de 30 victimes par catégorie : létalité non affichée",
                                scheme), puces
    return F.barres_categories(etiquettes, vals.round(2).tolist(), moy, scheme,
                               masques=masques_lib, libelle_moyenne="Moyenne",
                               titre_x="Vitesse maximale autorisée (km/h)" if col == "vma"
                               else None), puces



LUM_COURT = {"Jour": "Jour", "Aube ou crépuscule": "Aube, crépuscule",
             "Nuit éclairée": "Nuit éclairée", "Nuit non éclairée": "Nuit sans éclairage"}


@callback(Output(graph_id("s03-matrice"), "figure"), Output("s03-matrice-puces", "children"),
          Output("s03-matrice-titre", "children"),
          Output(graph_id("s03-jauge"), "figure"), Output("s03-jauge-puces", "children"),
          Output(graph_id("s03-annees"), "figure"), Output("s03-annees-titre", "children"),
          Output("s03-annees-puces", "children"), *ENTREES)
def matrice_jauge_annees(filtres, scheme):
    periode, dep, scheme = lire(filtres, scheme)
    puces = [chip_filtre(x) for x in da.puces_filtres(periode, dep)]
    # Matrice route × lumière
    m = da.filtrer(da.table("s03_matrice"), periode, dep).groupby(
        ["catr_groupe", "lum_groupe"], observed=True)[["tues", "victimes"]].sum()
    routes = [r for r in C.CATR_GROUPE_ORDRE if r != "Autre"]
    lums = C.LUM_GROUPE_ORDRE
    z, masque = [], []
    for r in routes:
        ligne_z, ligne_m = [], []
        for lu in lums:
            tv = m.loc[(r, lu)] if (r, lu) in m.index else None
            v = tv["victimes"] if tv is not None else 0
            ligne_z.append(letalite(tv["tues"], v) if v else float("nan"))
            ligne_m.append(v < SEUIL)
        z.append(ligne_z)
        masque.append(ligne_m)
    if all(all(lm) for lm in masque):
        fig_m = F.message_figure("Moins de 30 victimes par case : létalité non affichée", scheme)
        titre_m = "Route × lumière : létalité"
    else:
        fig_m = F.matrice(routes, [LUM_COURT[x] for x in lums], z, masque, scheme,
                          survol=" tués / 100 victimes")
        vis = [(z[i][j], routes[i], lums[j]) for i in range(len(routes)) for j in range(len(lums))
               if not masque[i][j]]
        v, r, lu = max(vis)
        titre_m = (f"{r}, {LUM_COURT[lu].lower()} : {fmt_number(v, 1)} tués pour 100 victimes")
    # Jauge : part des tués hors agglomération
    usa = da.filtrer(da.table("s02_gravite"), periode, dep).groupby("agg_lib")["tues"].sum()
    if usa.sum() < SEUIL:
        fig_j = F.message_figure("Moins de 30 tués sur ce périmètre", scheme)
    else:
        fig_j = F.anneau_jauge(usa.get("Hors agglomération", 0) / usa.sum() * 100,
                               "des tués, hors agglomération", scheme)
    # Barres 100 % par année
    g = da.filtrer(da.table("s02_gravite"), dep=dep, toutes_annees=True).pivot_table(
        index="annee", columns="agg_lib", values="tues", aggfunc="sum").reindex(C.ANNEES).fillna(0)
    tot = g.sum(axis=1)
    ok = tot >= SEUIL
    tk = tokens(scheme)
    if ok.sum() < 2:
        fig_a = F.message_figure("Moins de 30 tués par an sur ce périmètre", scheme)
        titre_a = "Tués selon le lieu, par année"
    else:
        hors = (g["Hors agglomération"] / tot * 100)[ok]
        en = (g["En agglomération"] / tot * 100)[ok]
        fig_a = F.barres_100([int(a) for a in hors.index],
                             {"Hors agglomération": hors.round(1).tolist(),
                              "En agglomération": en.round(1).tolist()},
                             {"Hors agglomération": tk["grav-tue"],
                              "En agglomération": tk["data-neutre"]}, scheme)
        lo, hi = hors.min(), hors.max()
        titre_a = (f"Hors agglomération, {fmt_pct(lo, 0)} à {fmt_pct(hi, 0)} des tués selon "
                   "l'année")
    p_toutes = [chip_filtre(x) for x in da.puces_filtres(None, dep, toutes_annees=True)]
    return fig_m, puces, titre_m, fig_j, puces, fig_a, titre_a, p_toutes
