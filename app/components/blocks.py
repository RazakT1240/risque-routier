"""Blocs de récit : en-tête de scène (§6.6), encart « Et alors ? » (§6.5), héros (§6.3),
triptyque d'accueil, navigation précédente / suivante (§6.7)."""

from __future__ import annotations

import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify


def scene_header(numero: int, nom: str, titre_debut: str, titre_accent: str = "",
                 chapeau: str = "") -> html.Header:
    """« 03 · LE PARADOXE » → h1 avec la seconde moitié en italique rouge → chapeau."""
    return html.Header(className="scene-header", children=[
        html.Div(f"{numero:02d} · {nom}", className="label"),
        html.H1([titre_debut, " " if titre_accent else "",
                 html.Span(titre_accent, className="titre-accent") if titre_accent else None],
                className="h1"),
        html.P(chapeau, className="body") if chapeau else None,
    ])


def insight(texte) -> html.Aside:
    return html.Aside(className="insight", children=[
        html.Div("Et alors ?", className="label"), html.P(texte)])


def hero(image_src: str, surtitre: str, nombre: str, legende: str, sous_texte: str,
         bouton_href: str, credit: str) -> html.Section:
    return html.Section(
        className="hero", style={"backgroundImage": f"url('{image_src}')"},
        role="img", **{"aria-label": f"{surtitre}. {nombre} {legende}. {sous_texte}"},
        children=[
            html.Div(className="hero-content", children=[
                html.Div(surtitre, className="label"),
                html.Div(nombre, className="hero-number"),
                html.Div(legende, className="hero-legende"),
                html.Div(sous_texte, className="hero-sub"),
                html.Div(dcc.Link(dmc.Button(
                    "Commencer", size="md",
                    rightSection=DashIconify(icon="tabler:arrow-right", width=18)),
                    href=bouton_href), style={"marginTop": 12}),
            ]),
            html.Div(credit, className="hero-credit"),
        ])


def triptyque(items: list[tuple[str, str, str]]) -> html.Div:
    """[(icône, mot-clé, ligne)]."""
    return html.Div(className="triptyque", children=[
        html.Div(className="carte", children=[
            DashIconify(icon=icon, width=22, className="t-accent"),
            html.Div(mot, className="h2", style={"marginTop": 8}),
            html.P(ligne, className="body", style={"margin": "6px 0 0"}),
        ]) for icon, mot, ligne in items])


def scene_nav(precedente: tuple[str, str] | None, suivante: tuple[str, str] | None):
    """(libellé, href) pour chaque bouton."""
    return html.Nav(className="scene-nav", **{"aria-label": "Navigation entre scènes"},
                    children=[
        dcc.Link(dmc.Button(f"Scène précédente · {precedente[0]}", variant="outline",
                            className="btn-precedent",
                            leftSection=DashIconify(icon="tabler:arrow-left", width=16)),
                 href=precedente[1]) if precedente else html.Span(),
        dcc.Link(dmc.Button(f"Scène suivante · {suivante[0]}", variant="light",
                            className="btn-suivant",
                            rightSection=DashIconify(icon="tabler:arrow-right", width=16)),
                 href=suivante[1]) if suivante else html.Span(),
    ])


def scene_layout(*blocs) -> dmc.Container:
    """Anatomie d'une scène : blocs empilés, 48 px entre blocs, contenu max 1280 px."""
    return dmc.Container(size=1280, px={"base": 16, "sm": 32}, py=40,
                         children=dmc.Stack(gap=48, children=[b for b in blocs if b]))
