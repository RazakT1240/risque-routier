"""Carte graphique (DESIGN_SYSTEM.md §6.4) : un seul graphique par carte.

En-tête : titre-message h2 + sous-titre de lecture + puce de filtre + menu ⋯ (agrandir,
télécharger PNG, voir les données). Pied : « Source : … · Définition : … ».
Les actions du menu sont branchées une fois pour toutes dans app/callbacks_globaux.py.
"""

from __future__ import annotations

import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify

GRAPH_CONFIG = {"displayModeBar": False, "responsive": True}


def graph_id(nom: str) -> dict:
    return {"type": "graph", "index": nom}


def menu_actions(nom: str) -> dmc.Menu:
    def item(action, label, icon):
        return dmc.MenuItem(label, id={"type": f"cc-{action}", "index": nom},
                            leftSection=DashIconify(icon=icon, width=16))
    return dmc.Menu(position="bottom-end", withinPortal=True, children=[
        dmc.MenuTarget(dmc.ActionIcon(
            DashIconify(icon="tabler:dots", width=18), variant="subtle", color="ardoise",
            **{"aria-label": "Actions du graphique"})),
        dmc.MenuDropdown([
            item("zoom", "Agrandir", "tabler:arrows-maximize"),
            item("png", "Télécharger en PNG", "tabler:download"),
            item("data", "Voir les données", "tabler:table"),
        ]),
    ])


def chip_filtre(texte: str, chip_id: dict | str | None = None, effacable: bool = False):
    enfants = [DashIconify(icon="tabler:filter", width=12), html.Span(texte)]
    if effacable:
        enfants.append(DashIconify(icon="tabler:x", width=12))
        return html.Button(enfants, id=chip_id or "chip-filtre", className="chip-filtre",
                           n_clicks=0, **{"aria-label": f"Retirer le filtre {texte}"})
    return html.Span(enfants, className="chip-info")


def chart_card(nom: str, titre, sous_titre: str, source: str, definition: str, *,
               figure=None, hauteur: int = 340, puces: list | None = None,
               controles=None, corps=None, aria: str | None = None) -> html.Section:
    """`corps` remplace le graphique (ex. message « effectif trop faible »)."""
    graphe = corps if corps is not None else dcc.Loading(
        type="dot", delay_show=300, color="var(--accent)",
        children=dcc.Graph(id=graph_id(nom), figure=figure, config=GRAPH_CONFIG,
                           style={"height": f"{hauteur}px"}, className="chart-graph"))
    return html.Section(className="carte chart-card", role="figure",
                        **{"aria-label": aria or (titre if isinstance(titre, str) else nom)},
                        children=[
        html.Div(className="chart-head", children=[
            html.Div(children=[
                html.H2(titre, className="h2"),
                html.Div(sous_titre, className="caption", style={"marginTop": 4}),
            ]),
            menu_actions(nom),
        ]),
        dmc.Group(gap=8, children=puces) if puces else None,
        controles,
        graphe,
        html.Div(className="chart-foot caption", children=[
            html.Span(f"Source : {source}"), html.Span(" · "),
            html.Span(f"Définition : {definition}")]),
    ])


def message_seuil(texte: str = "Moins de 30 victimes sur ce périmètre : taux non affiché"):
    return html.Div(className="seuil-msg", children=[
        DashIconify(icon="tabler:info-circle", width=18), html.Span(texte, style={
            "marginLeft": 8})])
