"""Démonstration du design system (phase 2) : couleurs, typos, boutons, figure Plotly.

Lancer : python sandbox/tokens_demo.py  ->  http://127.0.0.1:8051
Les données de la figure sont FACTICES et marquées comme telles.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import dash_mantine_components as dmc  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
from dash import Dash, Input, Output, dcc, html  # noqa: E402
from dash_iconify import DashIconify  # noqa: E402

from design.plotly_template import template_name  # noqa: E402
from design.theme import THEME  # noqa: E402
from design.tokens import FONTS_URL, LIGHT, tokens  # noqa: E402

INTERFACE = ["bg-page", "bg-surface", "bg-subtle", "border", "text-primary", "text-secondary",
             "text-muted", "accent", "accent-text"]
DONNEES = ["grav-tue", "grav-hospi", "grav-leger", "data-neutre", "data-neutre-clair",
           "delta-baisse", "delta-hausse", "seq-1", "seq-2", "seq-3", "seq-4", "seq-5", "seq-na"]


def swatches(names):
    return dmc.SimpleGrid(cols={"base": 2, "sm": 4, "lg": 7}, spacing="md", children=[
        html.Div([html.Div(className=f"swatch sw-{n}"), html.Div(n, className="caption")])
        for n in names])


def figure_factice(scheme: str) -> go.Figure:
    t = tokens(scheme)
    annees = list(range(2019, 2026))
    valeurs = [100, 80, 92, 101, 97, 98, 100]      # FACTICE
    fig = go.Figure(go.Bar(x=annees, y=valeurs, marker_color=[t["data-neutre"]] * 6
                           + [t["grav-tue"]], marker_line_width=0, marker_cornerradius=4,
                           text=valeurs, textposition="outside"))
    fig.update_layout(template=template_name(scheme), height=260,
                      yaxis=dict(showticklabels=False, showgrid=False))
    return fig


app = Dash(__name__, assets_folder=str(ROOT / "app" / "assets"),
           external_stylesheets=[FONTS_URL], title="Démo design system")

app.layout = dmc.MantineProvider(theme=THEME, defaultColorScheme="light", children=[
    dmc.Container(size=1280, py=48, children=dmc.Stack(gap=48, children=[
        dmc.Group(justify="space-between", children=[
            html.Div([html.Div("Phase 2 · Design system", className="label"),
                      html.H1(["La ville fait les accidents, ",
                               html.Span("la campagne fait les morts.",
                                         className="titre-accent")], className="h1")]),
            dmc.ColorSchemeToggle(id="theme-toggle",
                                  lightIcon=DashIconify(icon="tabler:moon", width=20),
                                  darkIcon=DashIconify(icon="tabler:sun", width=20),
                                  variant="default", size="lg",
                                  **{"aria-label": "Basculer le thème clair / sombre"}),
        ]),
        html.Section([html.Div("Couleurs d'interface", className="label"),
                      html.Div(style={"height": 12}), swatches(INTERFACE)]),
        html.Section([html.Div("Couleurs de données", className="label"),
                      html.Div(style={"height": 12}), swatches(DONNEES)]),
        html.Section(className="carte", children=dmc.Stack(gap=12, children=[
            html.Div("Typographie", className="label"),
            html.Div("3 263", className="display num"),
            html.H1("Titre-message de scène (h1)", className="h1"),
            html.H2("Titre de carte graphique (h2)", className="h2"),
            html.Div("12 345", className="kpi-value"),
            html.P("Texte de récit : chapeau d'une scène, une phrase claire et grave, sans "
                   "jargon, limitée à 68 caractères de large.", className="body recit"),
            html.Div("Libellé · sur-titre", className="label"),
            html.Div("Source : ONISR, fichiers BAAC 2019–2025 · légende", className="caption"),
            html.Div([html.Span("▲ +2,2 % vs 2024", className="delta-hausse"), " · ",
                      html.Span("▼ −1,4 % vs 2019", className="delta-baisse")],
                     className="kpi-deltas"),
        ])),
        html.Section(className="carte", children=dmc.Stack(gap=16, children=[
            html.Div("Boutons et contrôles", className="label"),
            dmc.Group([
                dmc.Button("Commencer", rightSection=DashIconify(icon="tabler:arrow-right")),
                dmc.Button("Scène suivante", variant="light",
                           rightSection=DashIconify(icon="tabler:arrow-right")),
                dmc.Button("Scène précédente", variant="outline", color="ardoise",
                           leftSection=DashIconify(icon="tabler:arrow-left")),
                dmc.Button("Désactivé", disabled=True),
            ]),
            dmc.SegmentedControl(data=["Vitesse autorisée", "Lumière", "Obstacle heurté"],
                                 value="Vitesse autorisée"),
            html.Div(className="insight", children=[
                html.Div("Et alors ?", className="label"),
                html.P("Encart d'exemple : deux lignes maximum, du point de vue de l'assureur.")]),
        ])),
        html.Section(className="carte", children=[
            dmc.Group(justify="space-between", children=[
                html.H2("Figure Plotly sur le template du mode", className="h2"),
                html.Span("Données factices", className="factice")]),
            dcc.Graph(id="demo-fig", config={"displayModeBar": False, "responsive": True},
                      figure=figure_factice("light")),
            html.Div("Source : données factices de démonstration", className="caption"),
        ]),
        html.Div(f"Fond de page clair : {LIGHT['bg-page']} (lu depuis tokens.py)",
                 className="caption"),
    ])),
])


@app.callback(Output("demo-fig", "figure"), Input("theme-toggle", "computedColorScheme"))
def maj_figure(scheme):
    return figure_factice(scheme or "light")


if __name__ == "__main__":
    # DASH_QA=1 : sans barre d'outils de debug (captures)
    app.run(debug=True, port=8051, dev_tools_ui=os.getenv("DASH_QA") != "1",
            dev_tools_disable_version_check=True)
