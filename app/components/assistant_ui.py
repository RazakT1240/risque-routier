"""Panneau « Assistant » : questions en langage naturel, réponses ancrées aux données.

Bouton flottant → tiroir (Drawer) avec un champ de recherche, des exemples cliquables et les
fiches récupérées (réponse chiffrée + source + lien vers la scène). Toute la logique de
récupération est dans `app.assistant` ; ici, uniquement l'affichage et les callbacks Dash.
"""

from __future__ import annotations

import dash_mantine_components as dmc
from dash import ALL, Input, Output, State, callback, ctx, dcc, html, no_update
from dash_iconify import DashIconify

from app import assistant as A
from app import i18n
from app.components.chart_card import GRAPH_CONFIG


def declencheur() -> html.Button:
    """Bouton d'action flottant (en bas à droite) qui ouvre le tiroir."""
    return html.Button(
        id="assistant-ouvrir", className="assistant-fab", n_clicks=0,
        **{"aria-label": i18n.t("assist.ouvrir_aria")},
        children=[DashIconify(icon="tabler:message-chatbot", width=22),
                  html.Span(i18n.t("assist.ouvrir"), className="assistant-fab-texte")])


def tiroir() -> dmc.Drawer:
    exemples = html.Div(className="assistant-exemples", children=[
        html.Button(q, id={"type": "assistant-exemple", "index": i}, n_clicks=0,
                    className="assistant-puce")
        for i, q in enumerate(A.EXEMPLES)])
    return dmc.Drawer(
        id="assistant-drawer", position="right", size=440, padding="lg", zIndex=400,
        withCloseButton=True, title=i18n.t("assist.titre"),
        children=html.Div(className="assistant-corps", children=[
            html.P(i18n.t("assist.intro"), className="caption assistant-intro"),
            dmc.Group(gap=8, wrap="nowrap", align="flex-end", children=[
                dmc.TextInput(
                    id="assistant-q", className="assistant-champ",
                    placeholder=i18n.t("assist.placeholder"),
                    leftSection=DashIconify(icon="tabler:search", width=16),
                    style={"flex": 1}, **{"aria-label": i18n.t("assist.q_aria")}),
                html.Button(DashIconify(icon="tabler:arrow-right", width=18),
                            id="assistant-go", n_clicks=0, className="assistant-go",
                            **{"aria-label": i18n.t("assist.chercher")}),
            ]),
            html.Div(i18n.t("assist.exemples"), className="assistant-sous-titre"),
            exemples,
            html.Div(id="assistant-reponses", className="assistant-reponses"),
        ]))


def _carte_reponse(f: dict, scheme: str) -> html.Div:
    figure = A.figure_fiche(f.get("graph"), scheme)
    graphe = dcc.Graph(figure=figure, config=GRAPH_CONFIG, className="assistant-graph",
                       style={"height": "190px"}) if figure is not None else None
    return html.Div(className="assistant-fiche", children=[
        html.Div(f["titre"], className="assistant-fiche-titre"),
        html.P(f["reponse"], className="assistant-fiche-rep"),
        graphe,
        html.Div(className="assistant-fiche-pied", children=[
            html.Span(f"{i18n.t('assist.source')} : {f['source']}", className="caption"),
            html.A([html.Span(f"{i18n.t('assist.voir')} « {f['scene_nom']} »"),
                    DashIconify(icon="tabler:arrow-up-right", width=14)],
                   href=f["scene_path"], className="assistant-lien"),
        ]),
    ])


def _resultats(question: str, scheme: str) -> html.Div:
    fiches = A.rechercher(question)
    if not fiches:
        return html.Div(className="assistant-vide", children=[
            DashIconify(icon="tabler:mood-empty", width=24, className="t-muted"),
            html.P(i18n.t("assist.vide"), className="caption")])
    cle = "assist.compteur_plus" if len(fiches) > 1 else "assist.compteur_une"
    return html.Div([
        html.Div(f"{len(fiches)} {i18n.t(cle)}", className="assistant-compteur"),
        *[_carte_reponse(f, scheme) for f in fiches],
    ])


def register(app) -> None:
    @callback(Output("assistant-drawer", "opened"),
              Input("assistant-ouvrir", "n_clicks"), prevent_initial_call=True)
    def ouvrir(_):
        return True

    @callback(Output("assistant-reponses", "children"), Output("assistant-q", "value"),
              Output("assistant-derniere", "data"),
              Input("assistant-go", "n_clicks"),
              Input({"type": "assistant-exemple", "index": ALL}, "n_clicks"),
              Input("assistant-q", "n_submit"),
              Input("theme-toggle", "computedColorScheme"),
              State("assistant-q", "value"), State("assistant-derniere", "data"),
              prevent_initial_call=True)
    def repondre(_go, _ex, _submit, scheme, valeur, derniere):
        scheme = scheme or "light"
        decl = ctx.triggered_id
        if isinstance(decl, dict) and decl.get("type") == "assistant-exemple":
            question = A.EXEMPLES[decl["index"]]
            return _resultats(question, scheme), question, question
        if decl == "theme-toggle":
            # Changement de thème : on redessine la dernière réponse aux bonnes couleurs
            if not derniere:
                return no_update, no_update, no_update
            return _resultats(derniere, scheme), no_update, no_update
        if not valeur:
            return no_update, no_update, no_update
        return _resultats(valeur, scheme), no_update, valeur


def widget() -> html.Div:
    return html.Div([declencheur(), tiroir(), dcc.Store(id="assistant-derniere")])
