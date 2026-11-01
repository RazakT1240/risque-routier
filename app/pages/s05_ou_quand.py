"""Scène 05 — Où et quand : territoires et moments les plus risqués."""

from __future__ import annotations

import dash
import numpy as np
import pandas as pd
from dash import Input, Output, callback, ctx, html, no_update

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
from app.components.format import fmt_number, fmt_ratio
from app.components.kpi_card import kpi_card, kpi_row
from app.components.scene_utils import ENTREES, SEUIL, lire
from app.scenes import voisines
from pipeline import config as C
from pipeline.indicators import letalite

dash.register_page(__name__, path="/ou-quand", name="Où et quand", order=5,
                   title="Où et quand · Risque routier")
NUM = 5
CUMUL = da.LIBELLE_PERIODE_CUMUL
CARTES = {"s05-carte-vict": ("taux_victimes_100k", "victimes pour 100 000 hab."),
          "s05-carte-tues": ("taux_tues_million", "tués par million d'hab.")}
METEO_LIB = {"pluie faible": "Pluie faible (0,2 à 5 mm)", "pluie forte": "Pluie forte (≥ 5 mm)",
             "gel": "Gel", "premiere_pluie": "Première pluie après 7 jours secs"}


def territoires() -> pd.DataFrame:
    t = da.table("ind_territoires")
    return t[t["periode"] == CUMUL].reset_index(drop=True)


def creneaux(periode, dep) -> pd.DataFrame:
    h = da.filtrer(da.table("s05_heatmap"), periode, dep)
    h = h.dropna(subset=["heure"])
    g = h.groupby(["jour_semaine", "heure"])[["accidents", "tues", "victimes"]].sum()
    return g.reindex(pd.MultiIndex.from_product([range(7), range(24)]), fill_value=0)


def _nuits_weekend(g: pd.DataFrame):
    nuits = g.loc[[(j, h) for j in (5, 6) for h in range(6)]].sum()
    tot = g.sum()
    return letalite(nuits["tues"], nuits["victimes"]), letalite(tot["tues"], tot["victimes"])


def titre():
    t = territoires().dropna(subset=["taux_tues_million"])
    ratio = t["taux_tues_million"].max() / t["taux_tues_million"].min()
    return ("Selon le département, le risque de mourir sur la route",
            f"varie de 1 à {fmt_number(ratio, 0)}.")


def titre_carte(col: str, quoi: str) -> str:
    t = territoires().dropna(subset=[col])
    return f"{t.loc[t[col].idxmax(), 'nom_dep']} compte le plus de {quoi} par habitant"


def titre_meteo() -> str:
    e = da.modele("meteo")["effets"]["pluie faible"]
    if e["ic_haut"] < 1:
        return "Les jours de pluie ne comptent pas plus d'accidents"
    if e["ic_bas"] > 1:
        return "Les jours de pluie comptent plus d'accidents"
    return "Pas d'effet mesurable de la pluie sur le nombre d'accidents"


def chapeau():
    nuit, moy = _nuits_weekend(creneaux(da.PERIODE_CUMUL, da.TERRITOIRE_FRANCE))
    m = da.modele("meteo")["effets"]
    pluie = m["pluie faible"]["rr"]
    phrase_pluie = ("la pluie, elle, n'augmente pas le nombre d'accidents" if pluie <= 1
                    else "la pluie augmente le nombre d'accidents")
    return (f"La nuit du week-end, {fmt_number(nuit, 1)} victimes sur 100 sont tuées, contre "
            f"{fmt_number(moy, 1)} en moyenne ; {phrase_pluie}.")


def et_alors():
    m = da.modele("meteo")["effets"]
    pp = m["premiere_pluie"]
    sig = not (pp["ic_bas"] <= 1 <= pp["ic_haut"])
    return ("Le lieu et l'heure font fortement varier la gravité : une offre « à l'usage » "
            "gagne à regarder quand et où l'on roule. "
            + ("La première pluie après une période sèche ressort comme un moment à risque."
               if sig and pp["rr"] > 1 else
               "La première pluie après une période sèche n'a pas d'effet significatif sur le "
               "nombre d'accidents."))


def legende(bornes, unite, avec_masques: bool):
    if len(bornes) < 2:
        return None
    items = [html.Span([html.Span(className=f"pastille leg-seq-{i + 1}"),
                        f"{fmt_number(bornes[i], 0)} – {fmt_number(bornes[i + 1], 0)}"])
             for i in range(len(bornes) - 1)]
    if avec_masques:
        items.append(html.Span([html.Span(className="pastille leg-seq-na"),
                                "effectif trop faible"]))
    return html.Div(className="legende-classes", children=[html.Span(unite), *items])


def layout(**_):
    debut, accent = titre()
    carte = lambda nom, titre_c, sous: chart_card(  # noqa: E731
        nom, titre_c, sous, f"{da.SOURCE_BAAC} ; {da.SOURCE_INSEE}",
        f"{CARTES[nom][1]}, cumul {CUMUL} (somme des populations annuelles) ; 5 classes par "
        "quantiles ; clic = filtrer le département", hauteur=420, mobile=True,
        legende=html.Div(id=f"{nom}-legende"))
    return scene_layout(
        scene_header(NUM, "Où et quand", debut, accent, chapeau()),
        html.Div(id="s05-kpis"),
        html.Div(className="grille-2", children=[
            carte("s05-carte-vict", titre_carte("taux_victimes_100k", "victimes"),
                  "Victimes pour 100 000 habitants et par an."),
            carte("s05-carte-tues", titre_carte("taux_tues_million", "tués"),
                  "Tués par million d'habitants et par an."),
        ]),
        html.Div(className="grille-2", children=[
            chart_card("s05-heatmap", "Accidents et létalité selon le jour et l'heure",
                       "Jour de la semaine × heure de l'accident ; plus la case est foncée, plus "
                       "la valeur est élevée.", da.SOURCE_BAAC,
                       "accidents corporels, ou létalité = tués / victimes × 100 ; cellules sous "
                       "30 victimes grisées", hauteur=340, mobile=True,
                       controles=bascule("s05-mode", ["Accidents", "Létalité"], "Létalité",
                                         "Mesure")),
            chart_card("s05-meteo", titre_meteo(),
                       "Risque relatif d'accident un jour donné, par rapport à un jour sec.",
                       f"{da.SOURCE_BAAC} ; Météo-France, données quotidiennes",
                       "GLM de Poisson (quasi-Poisson) sur le nombre d'accidents par "
                       "département-jour, effets fixes département, mois, année, jour de semaine ; "
                       "IC à 95 %", hauteur=340,
                       puces=[chip_filtre(f"Modèle national {CUMUL}")]),
        ]),
        insight(et_alors()),
        scene_nav(*voisines(NUM)),
    )


@callback(Output("s05-kpis", "children"), *ENTREES)
def kpis(filtres, scheme):
    periode, dep, _ = lire(filtres, scheme)
    t = territoires().dropna(subset=["taux_tues_million"]).sort_values("taux_tues_million")
    src_t = f"Source : {da.SOURCE_BAAC} ; {da.SOURCE_INSEE} · cumul {CUMUL}."
    haut, bas = t.iloc[-1], t.iloc[0]

    def carte_dep(kid, label, icon, ligne, rang_txt):
        return kpi_card(
            kid, label, icon, ligne["nom_dep"], texte=True,
            deltas=[{"texte": f"{fmt_number(ligne['taux_tues_million'], 0)} tués / million "
                              "d'hab. et par an", "sens": "neutre"}],
            leader=("tabler:map-pin", [rang_txt, html.B(ligne["dep"])]),
            lire=f"Tués rapportés à la population, cumulés sur {CUMUL} pour que chaque "
                 "département dépasse le seuil d'effectif.",
            assureur="Le risque mortel par habitant varie fortement d'un département à "
                     "l'autre : un argument pour un zonage fondé sur la gravité.", source=src_t)

    g = creneaux(periode, dep)
    # Tranches de 3 h : une case jour × heure seule est trop bruitée pour un KPI
    tr = g.groupby([g.index.get_level_values(0), g.index.get_level_values(1) // 3]).sum()
    ok = tr[tr["victimes"] >= SEUIL]
    k3 = None
    if len(ok):
        let = letalite(ok["tues"], ok["victimes"])
        j, h3 = let.idxmax()
        tot = g.sum()
        k3 = kpi_card(
            "s05-k3", "Créneau le plus létal", "tabler:clock",
            f"{C.JOURS[j]} {h3 * 3} h–{h3 * 3 + 3} h", texte=True,
            deltas=[{"texte": f"{fmt_number(let.max(), 1)} tués / 100 victimes", "sens": "neutre"}],
            leader=("tabler:chart-dots", ["Moyenne : ", html.B(fmt_number(letalite(
                tot["tues"], tot["victimes"]), 1))]),
            lire="Tranche de 3 heures où une victime est le plus souvent tuée (tranches d'au "
                 "moins 30 victimes).",
            assureur="Les heures de conduite comptent : un levier pour les offres à l'usage et "
                     "la prévention ciblée.",
            source=f"Source : {da.SOURCE_BAAC} · {da.libelle_territoire(dep)}.")
    if k3 is None:
        k3 = kpi_card("s05-k3", "Créneau le plus létal", "tabler:clock", "—",
                      lire="Aucun créneau n'atteint 30 victimes sur ce périmètre.",
                      assureur="Élargir la période ou le territoire.",
                      source=f"Source : {da.SOURCE_BAAC}.", indisponible=True)

    pp = da.modele("meteo")["effets"]["premiere_pluie"]
    sig = not (pp["ic_bas"] <= 1 <= pp["ic_haut"])
    k4 = kpi_card(
        "s05-k4", "Risque « première pluie »", "tabler:cloud-rain", fmt_ratio(pp["rr"], 2),
        deltas=[{"texte": f"IC 95 % : {fmt_number(pp['ic_bas'], 2)} – "
                          f"{fmt_number(pp['ic_haut'], 2)}", "sens": "neutre"}],
        leader=("tabler:info-circle", ["Effet ", html.B("significatif" if sig else
                                                        "non significatif")]),
        lire="Surcroît d'accidents un premier jour de pluie après au moins 7 jours secs, à "
             "département, mois, année et jour de semaine égaux.",
        assureur="Un effet faible ou nul : la météo seule ne justifie pas une alerte dédiée.",
        source=f"Source : modèle GLM national {CUMUL} ({da.SOURCE_BAAC} ; Météo-France).")
    return kpi_row([
        carte_dep("s05-k1", "Taux de tués maximal", "tabler:trending-up", haut,
                  f"Rang 1 sur {len(t)} · "),
        carte_dep("s05-k2", "Taux de tués minimal", "tabler:trending-down", bas,
                  f"Rang {len(t)} sur {len(t)} · "),
        k3, k4])


def _cartes(nom, dep, scheme):
    col, unite = CARTES[nom]
    t = territoires()
    sel = dep if dep != da.TERRITOIRE_FRANCE else None
    fig, bornes = F.choroplethe(da.geojson(), t["dep"].tolist(), t["nom_dep"].tolist(),
                                t[col].tolist(), scheme, unite, selection=sel)
    mob = F.barres_classees(t["nom_dep"].tolist(), t[col].astype(float).tolist(), scheme, unite)
    puces = [chip_filtre(f"{CUMUL} cumulé")]
    if sel:
        puces.append(chip_filtre(f"Filtre : {da.noms_departements().get(dep, dep)}",
                                 {"type": "s05-effacer", "index": nom}, effacable=True))
    return fig, mob, legende(bornes, f"{unite[0].upper()}{unite[1:]} :",
                             bool(t[col].isna().any())), puces


@callback(Output(graph_id("s05-carte-vict"), "figure"),
          Output(graph_id("s05-carte-vict-mobile"), "figure"),
          Output("s05-carte-vict-legende", "children"), Output("s05-carte-vict-puces", "children"),
          Output(graph_id("s05-carte-tues"), "figure"),
          Output(graph_id("s05-carte-tues-mobile"), "figure"),
          Output("s05-carte-tues-legende", "children"), Output("s05-carte-tues-puces", "children"),
          *ENTREES)
def cartes(filtres, scheme):
    _, dep, scheme = lire(filtres, scheme)
    return (*_cartes("s05-carte-vict", dep, scheme), *_cartes("s05-carte-tues", dep, scheme))


@callback(Output("filtre-territoire", "value", allow_duplicate=True),
          Input(graph_id("s05-carte-vict"), "clickData"),
          Input(graph_id("s05-carte-tues"), "clickData"),
          Input({"type": "s05-effacer", "index": dash.ALL}, "n_clicks"),
          prevent_initial_call=True)
def filtrer_par_clic(clic_v, clic_t, effacer):
    declencheur = ctx.triggered_id
    if isinstance(declencheur, dict) and declencheur.get("type") == "s05-effacer":
        return da.TERRITOIRE_FRANCE if any(effacer) else no_update
    clic = clic_v if declencheur == graph_id("s05-carte-vict") else clic_t
    try:
        return clic["points"][0]["location"]
    except (TypeError, KeyError, IndexError):
        return no_update


@callback(Output(graph_id("s05-heatmap"), "figure"),
          Output(graph_id("s05-heatmap-mobile"), "figure"),
          Output("s05-heatmap-puces", "children"), Output("s05-heatmap-titre", "children"),
          Input(bascule_id("s05-mode"), "value"), *ENTREES)
def heatmap(mode, filtres, scheme):
    periode, dep, scheme = lire(filtres, scheme)
    g = creneaux(periode, dep)
    puces = [chip_filtre(x) for x in da.puces_filtres(periode, dep)]
    if mode == "Accidents":
        z = g["accidents"].to_numpy().reshape(7, 24)
        masque = np.zeros_like(z, dtype=bool)
        fig = F.heatmap_jour_heure(z, masque, C.JOURS, scheme, "%{z:,.0f} accidents")
        par_h = g.groupby(level=1)["accidents"].sum()
        mob = F.barres_heure(list(range(24)), par_h.tolist(), scheme)
        titre_h = (f"Les accidents culminent vers {int(par_h.idxmax())} h"
                   if par_h.sum() else "Accidents selon le jour et l'heure")
    else:
        let = letalite(g["tues"], g["victimes"].replace(0, np.nan))
        z = let.to_numpy().reshape(7, 24)
        masque = (g["victimes"] < SEUIL).to_numpy().reshape(7, 24)
        fig = F.heatmap_jour_heure(z, masque, C.JOURS, scheme, "%{z:.1f} tués / 100 victimes")
        par_h = g.groupby(level=1)[["tues", "victimes"]].sum()
        vals = letalite(par_h["tues"], par_h["victimes"]).where(par_h["victimes"] >= SEUIL)
        mob = F.barres_heure(list(range(24)), vals.tolist(), scheme,
                             fmt=lambda v: fmt_number(v, 1))
        nuit = par_h.loc[0:5].sum()
        jour = par_h.loc[6:23].sum()
        titre_h = "Létalité selon le jour et l'heure"
        if nuit["victimes"] >= SEUIL and jour["victimes"] >= SEUIL:
            fois = (letalite(nuit["tues"], nuit["victimes"])
                    / letalite(jour["tues"], jour["victimes"]))
            if fois >= 1.2:
                titre_h = (f"Entre minuit et 6 h, une victime est {fmt_number(fois, 1)} fois "
                           "plus souvent tuée")
        if masque.all():
            fig = F.message_figure("Moins de 30 victimes par créneau : létalité non affichée",
                                   scheme)
    return fig, mob, puces, titre_h


@callback(Output(graph_id("s05-meteo"), "figure"), *ENTREES)
def meteo(filtres, scheme):
    _, _, scheme = lire(filtres, scheme)
    e = da.modele("meteo")["effets"]
    cles = ["pluie faible", "pluie forte", "gel", "premiere_pluie"]
    rr = [e[k]["rr"] for k in cles]
    signif = [k for k in cles if not (e[k]["ic_bas"] <= 1 <= e[k]["ic_haut"]) and e[k]["rr"] > 1]
    alerte = METEO_LIB[max(signif, key=lambda k: e[k]["rr"])] if signif else None
    return F.risques_relatifs([METEO_LIB[k] for k in cles], rr, [e[k]["ic_bas"] for k in cles],
                              [e[k]["ic_haut"] for k in cles], scheme, alerte=alerte)
