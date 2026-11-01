"""Scène 01 — Accueil : carte héros, triptyque Fréquence · Gravité · Coût."""

from __future__ import annotations

import calendar

import dash
from dash import html

from app import data_access as da
from app.components.blocks import bande_usagers, hero, scene_layout, triptyque
from app.components.format import INSECABLE, fmt_number, fmt_pct
from app.components.scene_utils import par_annee
from pipeline.indicators import letalite

# (illustration, libellé, type_usager dans les données)
USAGERS = [("voiture", "Voiture", "Voiture"), ("moto", "Deux-roues motorisés", "2RM"),
           ("pieton", "Piétons", "Piéton"), ("velo", "Vélos", "Vélo"),
           ("camion", "Poids lourds", "Poids lourd")]

dash.register_page(__name__, path="/", name="Accueil", order=1,
                   title="Risque routier · fréquence, gravité, coût")


def _chiffres():
    a1 = da.DERNIERE_ANNEE
    s = par_annee("s02_gravite", da.TERRITOIRE_FRANCE, ["tues"])["tues"]
    acc = da.filtre_table("s02_accidents", str(a1)).groupby("agg_lib")["accidents"].sum()
    usa = da.filtre_table("s02_gravite", str(a1)).groupby("agg_lib")[
        ["tues", "victimes"]].sum()
    jours = 366 if calendar.isleap(a1) else 365
    return {
        "annee": a1, "tues": s[a1], "par_jour": s[a1] / jours,
        "accidents": acc.sum(), "part_en": acc.get("En agglomération", 0) / acc.sum() * 100,
        "let_hors": letalite(usa.loc["Hors agglomération", "tues"],
                             usa.loc["Hors agglomération", "victimes"]),
        "let_en": letalite(usa.loc["En agglomération", "tues"],
                           usa.loc["En agglomération", "victimes"]),
    }


def cout_annuel(annee: int) -> float | None:
    """Coût socio-économique total = victimes × valeurs tutélaires (G1, G8)."""
    vt = (da.references() or {}).get("valeurs_tutelaires_eur") or {}
    if vt.get("tue") is None or not vt.get("source"):
        return None
    g = da.filtre_table("s02_gravite", str(annee))[["tues", "hospitalises", "legers"]].sum()
    return (g["tues"] * vt["tue"] + g["hospitalises"] * vt["blesse_hospitalise"]
            + g["legers"] * vt["blesse_leger"])


def ligne_cout(annee: int) -> str:
    vt = (da.references() or {}).get("valeurs_tutelaires_eur") or {}
    cout = cout_annuel(annee)
    if cout is None:
        return ("Coût socio-économique : À renseigner (valeur tutélaire à sourcer, "
                "voir la page Méthode).")
    return (f"{fmt_number(cout / 1e9, 1)}{INSECABLE}Md€ de coût socio-économique en {annee} — "
            f"soit {fmt_number(vt['tue'] / 1e6, 1)}{INSECABLE}M€ par vie perdue "
            f"(valeur tutélaire ONISR {vt.get('annee_reference')}).")


def _usagers():
    """Part des tués par mode d'usager, sur toute la période (cumul, G5/G1)."""
    g = da.table("s02_gravite")
    tot = g["tues"].sum()
    par_mode = g.groupby("type_usager")["tues"].sum()
    pire = par_mode.reindex([u[2] for u in USAGERS]).idxmax()
    items = []
    for fichier, libelle, mode in USAGERS:
        part = par_mode.get(mode, 0) / tot * 100
        items.append((fichier, libelle, f"{fmt_pct(part, 0)} des tués", mode == pire))
    return items


def layout(**_):
    c = _chiffres()
    return scene_layout(
        hero("/assets/hero-route-nuit.svg",
             "Sécurité routière · France métropolitaine · 2019–2025",
             fmt_number(c["tues"], milliers=INSECABLE), f"personnes tuées sur la route en "
             f"{c['annee']}", f"soit {fmt_number(c['par_jour'], 1)} par jour",
             "/vue-ensemble", "Illustration générée pour ce projet"),
        html.Div(className="scene-header", children=[
            html.Div("Le propos", className="label"),
            html.P("Le nombre d'accidents ne dit pas où est le risque. Pour un assureur, le "
                   "risque corporel, c'est la fréquence multipliée par la gravité, et les deux "
                   "ne sont pas au même endroit.", className="body recit"),
        ]),
        triptyque([
            ("tabler:repeat", "Fréquence",
             f"{fmt_number(c['accidents'])} accidents corporels en {c['annee']}, dont "
             f"{fmt_pct(c['part_en'], 0)} en agglomération."),
            ("tabler:alert-triangle", "Gravité",
             f"Hors agglomération, {fmt_number(c['let_hors'], 1)} tués pour 100 victimes, contre "
             f"{fmt_number(c['let_en'], 1)} en ville."),
            ("tabler:coin-euro", "Coût", ligne_cout(c["annee"])),
        ]),
        bande_usagers(
            "Qui paie le plus lourd tribut ?",
            f"Part de chaque mode dans les tués, sur {da.LIBELLE_PERIODE_CUMUL}.",
            _usagers(), da.SOURCE_BAAC),
    )
