"""Composants en isolation (phase 3) : coquille, en-tête de scène, KPI retournables, carte
graphique, bascule, encart, héros, triptyque, navigation, états.

TOUTES LES VALEURS DE CETTE PAGE SONT FACTICES et affichées comme telles.
Lancer : python sandbox/components_demo.py  ->  http://127.0.0.1:8052
  /           : carte héros + triptyque
  /paradoxe   : scène type (KPI, graphique, encart, navigation)
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import dash_mantine_components as dmc  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
from dash import Dash, Input, Output, dcc, html  # noqa: E402

from app import callbacks_globaux  # noqa: E402
from app.components import shell  # noqa: E402
from app.components.blocks import (  # noqa: E402
    bascule,
    bascule_id,
    hero,
    insight,
    scene_header,
    scene_layout,
    scene_nav,
    triptyque,
)
from app.components.chart_card import chart_card, chip_filtre, message_seuil  # noqa: E402
from app.components.format import INSECABLE, delta, fmt_number, fmt_pct  # noqa: E402
from app.components.kpi_card import kpi_card, kpi_row  # noqa: E402
from design.plotly_template import template_name  # noqa: E402
from design.theme import THEME  # noqa: E402
from design.tokens import FONTS_URL, tokens  # noqa: E402

FACTICE = html.Span("Données factices", className="factice")
ANNEES = list(range(2019, 2026))
DEPS_FACTICES = [{"dep": "01", "nom": "Département factice A"},
                 {"dep": "02", "nom": "Département factice B"}]
SERIE = [100, 82, 95, 104, 99, 101, 103]          # FACTICE


def kpis():
    def carte(i, label, icon, v, ref1, ref0, leader, mauvais=True):
        return kpi_card(
            f"kpi-demo-{i}", label, icon, fmt_number(v), compte=v,
            deltas=[delta(v, ref1, "2024", mauvais), delta(v, ref0, "2019", mauvais)],
            leader=(icon, ["Segment factice au libellé volontairement très long : ",
                          html.B(fmt_pct(31.4)), " du total"]),
            spark=[x * v / 100 for x in SERIE],
            lire="Définition factice d'une ligne : ce que mesure l'indicateur.",
            assureur="Lecture assureur factice : ce que cela change pour la sinistralité.",
            source="Source : données factices de démonstration.")
    return kpi_row([
        carte(1, "Tués · 2025 (factice)", "tabler:cross", 3263, 3193, 3244, None),
        carte(2, "Hospitalisés · 2025 (factice)", "tabler:building-hospital", 18345, 17831,
              19609, None),
        carte(3, "Létalité (factice)", "tabler:percentage", 4750, 4710, 4400, None),
        kpi_card("kpi-demo-4", "Taux (factice)", "tabler:map-pin", "—", indisponible=True,
                 lire="Exemple de donnée indisponible : tiret et infobulle.",
                 assureur="Jamais de valeur inventée (G1).", source="Source : factice."),
    ])


def figure(vue: str, scheme: str) -> go.Figure:
    t = tokens(scheme)
    if vue == "Courbe":
        fig = go.Figure(go.Scatter(x=ANNEES, y=SERIE, mode="lines+markers",
                                   line=dict(color=t["data-neutre"], width=2),
                                   marker=dict(color=[t["data-neutre"]] * 6 + [t["grav-tue"]],
                                               size=[0] * 6 + [9])))
        fig.add_vrect(x0=2019.5, x1=2020.5, fillcolor=t["data-neutre-clair"], opacity=0.35,
                      line_width=0, annotation_text="Confinements",
                      annotation_position="top left")
        fig.update_layout(hovermode="x unified")
    else:
        fig = go.Figure(go.Bar(x=ANNEES, y=SERIE, marker_line_width=0, marker_cornerradius=4,
                               marker_color=[t["data-neutre"]] * 6 + [t["grav-tue"]],
                               text=SERIE, textposition="outside", cliponaxis=False))
        fig.update_yaxes(showticklabels=False, showgrid=False)
    fig.update_layout(template=template_name(scheme), margin=dict(l=8, r=8, t=24, b=8))
    return fig


def page_scene():
    return scene_layout(
        dmc.Group(justify="space-between", children=[FACTICE]),
        scene_header(3, "Le paradoxe", "La ville fait les accidents,",
                     "la campagne fait les morts.",
                     "Chapeau factice : une phrase qui pose la question de la scène."),
        kpis(),
        dmc.SimpleGrid(cols={"base": 1, "lg": 2}, spacing="lg", children=[
            chart_card("demo-fig", "Titre-message de carte (factice)",
                       "Sous-titre de lecture : ce qu'il faut regarder.",
                       "données factices", "valeur fictive, base 100 en 2019",
                       figure=figure("Barres", "light"),
                       puces=[chip_filtre("Toutes années"),
                              chip_filtre("Filtre : Département factice A", "chip-demo",
                                          effacable=True)],
                       controles=bascule("demo-bascule", ["Barres", "Courbe"], "Barres",
                                         "Type de graphique")),
            chart_card("demo-vide", "État « effectif trop faible » (factice)",
                       "Le taux n'est pas affiché sous 30 victimes.",
                       "données factices", "taux fictif", corps=message_seuil()),
        ]),
        insight("Encart factice : deux lignes maximum, du point de vue de l'assureur, "
                "qui disent quoi faire du constat."),
        scene_nav(("Accueil", "/"), ("Qui", "/qui")),
    )


def page_heros():
    return scene_layout(
        hero("/assets/hero-route-nuit.svg",
             "Sécurité routière · France métropolitaine · 2019–2025",
             fmt_number(3263, milliers=INSECABLE), "tués en 2025 (valeur factice)",
             "soit 8,9 par jour (factice)",
             "/paradoxe", "Illustration générée pour ce projet"),
        triptyque([("tabler:repeat", "Fréquence", "Ligne factice : combien d'accidents."),
                   ("tabler:alert-triangle", "Gravité", "Ligne factice : à quel point."),
                   ("tabler:coin-euro", "Coût", "Ligne factice : ce que cela coûte.")]),
    )


app = Dash(__name__, assets_folder=str(ROOT / "app" / "assets"),
           external_stylesheets=[FONTS_URL], title="Composants · démo factice",
           suppress_callback_exceptions=True)

app.layout = dmc.MantineProvider(theme=THEME, defaultColorScheme="light", children=[
    dcc.Location(id="url"),
    *callbacks_globaux.stores(),
    shell.app_shell(html.Div(id="page"), ANNEES, DEPS_FACTICES, 2025),
    callbacks_globaux.modales(),
])
callbacks_globaux.register(app)
shell.register(app)


@app.callback(Output("page", "children"), Output("progress-rule", "style"),
              Output("scene-compteur", "children"), Input("url", "pathname"))
def router(path):
    if path == "/paradoxe":
        return page_scene(), {"width": f"{300 / 8:.1f}%"}, "Scène 3 / 8 (démo)"
    return page_heros(), {"width": f"{100 / 8:.1f}%"}, "Scène 1 / 8 (démo)"


@app.callback(Output({"type": "graph", "index": "demo-fig"}, "figure"),
              Input(bascule_id("demo-bascule"), "value"),
              Input("theme-toggle", "computedColorScheme"))
def maj(vue, scheme):
    return figure(vue or "Barres", scheme or "light")


if __name__ == "__main__":
    app.run(debug=True, port=8052, dev_tools_ui=os.getenv("DASH_QA") != "1",
            dev_tools_disable_version_check=True)
