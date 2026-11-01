"""Page introuvable (interface en français)."""

import dash
from dash import html

from app.components.blocks import lien_bouton, scene_layout

dash.register_page(__name__, path="/404", title="Page introuvable · Risque routier")


def layout(**_):
    return scene_layout(html.Div(className="scene-header", children=[
        html.Div("Erreur 404", className="label"),
        html.H1("Cette page n'existe pas.", className="h1"),
        html.P("Le lien suivi ne correspond à aucune scène du récit.", className="body"),
        html.Div(lien_bouton("Revenir à l'accueil", "/", "btn-primaire",
                             icone_g="tabler:arrow-left")),
    ]))
