"""Callbacks partagés par toutes les pages : actions du menu ⋯ des cartes graphiques.

- Agrandir : copie la figure dans une modale plein écran.
- Télécharger en PNG : Plotly.downloadImage côté client.
- Voir les données : tableau construit depuis les traces de la figure.
"""

from __future__ import annotations

import dash_mantine_components as dmc
from dash import ALL, MATCH, Input, Output, State, clientside_callback, ctx, dcc, html, no_update

from app.components.chart_card import GRAPH_CONFIG
from app.components.format import fmt_number

MAX_LIGNES = 400


def modales() -> html.Div:
    return html.Div([
        dmc.Modal(id="modal-zoom", size="90%", centered=True, title="", children=dcc.Graph(
            id="modal-graph", config=GRAPH_CONFIG, style={"height": "70vh"})),
        dmc.Modal(id="modal-data", size="lg", centered=True, title="Données du graphique",
                  children=html.Div(id="modal-data-body")),
    ])


def _figure_par_index(index, figures, ids):
    for fig, gid in zip(figures, ids, strict=False):
        if gid["index"] == index:
            return fig
    return None


def _valeur(v):
    if isinstance(v, bool) or v is None:
        return "" if v is None else str(v)
    if isinstance(v, float):
        return fmt_number(v, 0 if v.is_integer() else 1)
    if isinstance(v, int):
        return fmt_number(v)
    return str(v)


def table_depuis_figure(fig: dict) -> list[list]:
    lignes = []
    for tr in fig.get("data", []):
        nom = tr.get("name") or ""
        if "locations" in tr:
            lignes += [[nom, loc, z] for loc, z in zip(tr["locations"], tr.get("z", []),
                                                       strict=False)]
        elif tr.get("type") == "heatmap":
            xs, ys, zs = tr.get("x", []), tr.get("y", []), tr.get("z", [])
            lignes += [[f"{y}", x, zs[i][j]] for i, y in enumerate(ys)
                       for j, x in enumerate(xs) if i < len(zs) and j < len(zs[i])]
        else:
            xs, ys = tr.get("x") or [], tr.get("y") or []
            lignes += [[nom, x, y] for x, y in zip(xs, ys, strict=False)]
    return lignes[:MAX_LIGNES]


def register(app) -> None:
    @app.callback(
        Output("modal-zoom", "opened"), Output("modal-graph", "figure"),
        Output("modal-zoom", "title"),
        Input({"type": "cc-zoom", "index": ALL}, "n_clicks"),
        State({"type": "graph", "index": ALL}, "figure"),
        State({"type": "graph", "index": ALL}, "id"),
        State({"type": "cc-titre", "index": ALL}, "children"),
        State({"type": "cc-titre", "index": ALL}, "id"),
        prevent_initial_call=True)
    def agrandir(clics, figures, ids, titres, ids_titres):
        if not ctx.triggered_id or not any(clics):
            return no_update, no_update, no_update
        index = ctx.triggered_id["index"]
        fig = _figure_par_index(index, figures, ids)
        titre = next((tt for tt, i in zip(titres, ids_titres, strict=False)
                      if i["index"] == index), "")
        return (True, fig, titre) if fig else (no_update, no_update, no_update)

    @app.callback(
        Output("modal-data", "opened"), Output("modal-data-body", "children"),
        Input({"type": "cc-data", "index": ALL}, "n_clicks"),
        State({"type": "graph", "index": ALL}, "figure"),
        State({"type": "graph", "index": ALL}, "id"),
        prevent_initial_call=True)
    def voir_donnees(clics, figures, ids):
        if not ctx.triggered_id or not any(clics):
            return no_update, no_update
        fig = _figure_par_index(ctx.triggered_id["index"], figures, ids)
        if not fig:
            return no_update, no_update
        lignes = table_depuis_figure(fig)
        if not lignes:
            return True, html.P("Données non tabulables pour ce graphique.", className="body")
        avec_serie = any(ligne[0] for ligne in lignes)
        tete = (["Série"] if avec_serie else []) + ["Catégorie", "Valeur"]
        corps = [([str(s)] if avec_serie else []) + [str(c), _valeur(v)]
                 for s, c, v in lignes]
        note = (html.P(f"{MAX_LIGNES} premières lignes affichées.", className="caption")
                if len(lignes) >= MAX_LIGNES else None)
        return True, html.Div([note, dmc.ScrollArea(h=420, children=dmc.Table(
            striped=True, highlightOnHover=True, data={"head": tete, "body": corps}))])

    clientside_callback(
        """
        function(clics) {
            const t = window.dash_clientside.callback_context.triggered_id;
            if (!t || !clics.some(Boolean)) { return window.dash_clientside.no_update; }
            const id = JSON.stringify({index: t.index, type: "graph"});
            const conteneur = document.getElementById(id);
            const gd = conteneur && conteneur.querySelector(".js-plotly-plot");
            if (gd && window.routeExportPng) { window.routeExportPng(gd, t.index); }
            return window.dash_clientside.no_update;
        }
        """,
        Output("png-sink", "data"),
        Input({"type": "cc-png", "index": ALL}, "n_clicks"),
        prevent_initial_call=True)

    # Bascule : le Select mobile recopie sa valeur dans le SegmentedControl (source unique)
    clientside_callback(
        "function(v) { return v || window.dash_clientside.no_update; }",
        Output({"type": "bascule", "index": MATCH}, "value"),
        Input({"type": "bascule-mobile", "index": MATCH}, "value"),
        prevent_initial_call=True)


def stores() -> list:
    return [dcc.Store(id="png-sink")]
