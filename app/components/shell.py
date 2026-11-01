"""Coquille de l'application : header (§6.1), filtres globaux (BRIEF §4), navbar (§6.7)."""

from __future__ import annotations

import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

from app.scenes import SCENES

PERIODE_CUMUL = "cumul"
TERRITOIRE_FRANCE = "FR"


def filtre(label: str, icon: str, composant) -> html.Div:
    return html.Div(children=[
        html.Div(className="filtre-label", children=[
            DashIconify(icon=icon, width=12, className="t-secondary"),
            html.Span(label, className="label", style={"fontSize": 11, "lineHeight": "14px"})]),
        composant])


def filtres(annees: list[int], departements: list[dict], annee_defaut: int) -> dmc.Group:
    periode = dmc.Select(
        id="filtre-periode", size="xs", w=150, allowDeselect=False,
        value=str(annee_defaut), comboboxProps={"withinPortal": True},
        data=[{"value": PERIODE_CUMUL, "label": f"{annees[0]}–{annees[-1]} (cumul)"}]
        + [{"value": str(a), "label": str(a)} for a in reversed(annees)],
        **{"aria-label": "Période"})
    territoire = dmc.Select(
        id="filtre-territoire", size="xs", w=210, searchable=True, allowDeselect=False,
        value=TERRITOIRE_FRANCE, nothingFoundMessage="Aucun département",
        comboboxProps={"withinPortal": True}, maxDropdownHeight=320,
        data=[{"value": TERRITOIRE_FRANCE, "label": "France métropolitaine"}]
        + [{"value": d["dep"], "label": f"{d['dep']} · {d['nom']}"} for d in departements],
        **{"aria-label": "Territoire"})
    return dmc.Group(gap=12, wrap="nowrap", children=[
        filtre("Période", "tabler:calendar", periode),
        filtre("Territoire", "tabler:map-2", territoire),
    ])


def header(annees, departements, annee_defaut) -> dmc.AppShellHeader:
    return dmc.AppShellHeader(className="app-header", children=[
        html.Div(className="header-inner", children=[
            dmc.Group(gap=12, wrap="nowrap", children=[
                dmc.Burger(id="burger", size="sm", hiddenFrom="sm",
                           **{"aria-label": "Ouvrir la navigation"}),
                html.Div("R", className="monogramme", **{"aria-hidden": "true"}),
                html.Div(className="brand-text", children=[
                    html.Div("Risque routier", className="brand-title"),
                    html.Div("Fréquence · Gravité · Coût", className="label",
                             style={"fontSize": 10, "lineHeight": "12px"}),
                ]),
            ]),
            html.Div(id="scene-compteur", className="caption header-centre"),
            dmc.Group(gap=16, wrap="nowrap", children=[
                html.Div(filtres(annees, departements, annee_defaut), className="header-filtres"),
                dmc.ColorSchemeToggle(
                    id="theme-toggle", variant="default", size="lg",
                    lightIcon=DashIconify(icon="tabler:moon", width=18),
                    darkIcon=DashIconify(icon="tabler:sun", width=18),
                    **{"aria-label": "Basculer le thème clair / sombre"}),
            ]),
        ]),
        html.Div(className="progress-track", children=html.Div(
            id="progress-rule", className="progress-rule", style={"width": "0%"})),
    ])


def navbar() -> dmc.AppShellNavbar:
    return dmc.AppShellNavbar(className="app-navbar", p="md", children=dmc.Stack(gap=4, children=[
        html.Div("Challenge Dataviz · Institut des Actuaires", className="nav-badge"),
        html.Div(style={"height": 12}),
        *[dmc.NavLink(
            href=s["path"], active="exact", className="nav-link",
            label=html.Span(s["nom"]),
            leftSection=dmc.Group(gap=8, wrap="nowrap", children=[
                html.Span(f"{s['num']:02d}", className="nav-num"),
                DashIconify(icon=s["icon"], width=18)]),
        ) for s in SCENES],
        html.Div(style={"flex": 1}),
    ]))
