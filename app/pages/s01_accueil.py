"""Scène 01 — Accueil : carte héros, triptyque Fréquence · Gravité · Coût."""

from __future__ import annotations

import calendar

import dash
from dash import html

from app import data_access as da
from app.components.blocks import hero, scene_layout, triptyque
from app.components.format import INSECABLE, fmt_number, fmt_pct
from app.components.scene_utils import par_annee
from pipeline.indicators import letalite

dash.register_page(__name__, path="/", name="Accueil", order=1,
                   title="Risque routier · fréquence, gravité, coût")


def _chiffres():
    a1 = da.DERNIERE_ANNEE
    s = par_annee("s02_gravite", da.TERRITOIRE_FRANCE, ["tues"])["tues"]
    acc = da.filtrer(da.table("s02_accidents"), str(a1)).groupby("agg_lib")["accidents"].sum()
    usa = da.filtrer(da.table("s02_gravite"), str(a1)).groupby("agg_lib")[
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


def ligne_cout() -> str:
    vt = (da.references() or {}).get("valeurs_tutelaires_eur") or {}
    if vt.get("tue") is None or not vt.get("source"):
        return ("Coût socio-économique d'un tué : À renseigner (valeur tutélaire à sourcer, "
                "voir la page Méthode).")
    return (f"Un tué représente {fmt_number(vt['tue'] / 1e6, 1)}{INSECABLE}M€ de coût "
            f"socio-économique (valeur tutélaire {vt.get('annee_reference')}).")


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
            ("tabler:coin-euro", "Coût", ligne_cout()),
        ]),
    )
