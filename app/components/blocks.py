"""Blocs de récit : en-tête de scène (§6.6), encart « Et alors ? » (§6.5), héros (§6.3),
triptyque d'accueil, navigation précédente / suivante (§6.7)."""

from __future__ import annotations

import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify

from app import i18n


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
        html.Div(i18n.t("insight.label"), className="label"), html.P(texte)])


def lien_bouton(texte: str, href: str, classe: str, icone_g: str | None = None,
                icone_d: str | None = None) -> dcc.Link:
    """Lien stylé en bouton : un seul arrêt de tabulation (pas de <a><button>)."""
    return dcc.Link(href=href, className=f"btn {classe}", children=[
        DashIconify(icon=icone_g, width=16) if icone_g else None, html.Span(texte),
        DashIconify(icon=icone_d, width=16) if icone_d else None])


def hero(image_src: str, surtitre: str, nombre: str, legende: str, sous_texte: str,
         bouton_href: str, credit: str) -> html.Section:
    return html.Section(
        className="hero", style={"backgroundImage": f"url('{image_src}')"},
        **{"aria-label": "Introduction"},
        children=[
            html.Div(className="hero-content", children=[
                html.Div(surtitre, className="label"),
                html.Div(nombre, className="hero-number"),
                html.Div(legende, className="hero-legende"),
                html.Div(sous_texte, className="hero-sub"),
                html.Div(lien_bouton("Commencer", bouton_href, "btn-primaire btn-lg",
                                     icone_d="tabler:arrow-right"), style={"marginTop": 12}),
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


def bande_usagers(titre: str, sous_titre: str, items: list[tuple[str, str, str, bool]],
                  source: str) -> html.Section:
    """Bande illustrée des usagers de la route : illustration « 3D » + part chiffrée (G1).

    `items` = [(fichier_svg, libellé, valeur, alerte)] ; `alerte=True` met la carte en relief."""
    cartes = [
        html.Figure(className="usager" + (" usager-alerte" if alerte else ""), children=[
            html.Img(src=f"/assets/vehicules/{fichier}.svg", className="usager-img",
                     alt=f"Illustration : {libelle}"),
            html.Figcaption(children=[
                html.Span(libelle, className="usager-nom"),
                html.Span(valeur, className="usager-val"),
            ]),
        ]) for fichier, libelle, valeur, alerte in items]
    return html.Section(className="carte bande-usagers", **{"aria-label": titre}, children=[
        html.Div(className="chart-head", children=[html.Div(children=[
            html.H2(titre, className="h2"),
            html.Div(sous_titre, className="caption", style={"marginTop": 4})])]),
        html.Div(className="usagers-grille", children=cartes),
        html.Div(className="chart-foot caption", children=f"Source : {source}"),
    ])


def scene_nav(precedente: tuple[str, str] | None, suivante: tuple[str, str] | None):
    """(libellé, href) par bouton ; un pont narratif (i18n.pont) précède le « suivant »."""
    pont = i18n.pont(suivante[1]) if suivante else None
    boutons = html.Div(className="scene-nav-row", children=[
        lien_bouton(f"{i18n.t('nav.precedente')} · {i18n.nom_scene(precedente[1])}",
                    precedente[1], "btn-precedent",
                    icone_g="tabler:arrow-left") if precedente else html.Span(),
        lien_bouton(f"{i18n.t('nav.suivante')} · {i18n.nom_scene(suivante[1])}",
                    suivante[1], "btn-suivant",
                    icone_d="tabler:arrow-right") if suivante else html.Span(),
    ])
    return html.Nav(className="scene-nav", **{"aria-label": i18n.t("nav.aria")}, children=[
        html.P(pont, className="scene-pont") if pont else None, boutons])


def bascule_id(nom: str) -> dict:
    """Identifiant à lire dans les callbacks : Input(bascule_id(nom), "value")."""
    return {"type": "bascule", "index": nom}


def bascule(nom: str, options: list[str], valeur: str, label: str) -> html.Div:
    """SegmentedControl sur écran large, Select sous 768 px (pas de débordement sur mobile).

    Le Select mobile recopie sa valeur dans le SegmentedControl (callback global), qui reste
    la seule source lue par les callbacks."""
    return html.Div(children=[
        dmc.SegmentedControl(id=bascule_id(nom), data=options, value=valeur, visibleFrom="sm",
                             **{"aria-label": label}),
        dmc.Select(id={"type": "bascule-mobile", "index": nom}, data=options, value=valeur,
                   hiddenFrom="sm", allowDeselect=False, comboboxProps={"withinPortal": True},
                   **{"aria-label": label}),
    ])


def scene_layout(*blocs) -> dmc.Container:
    """Anatomie d'une scène : blocs empilés, 48 px entre blocs, contenu max 1280 px."""
    return dmc.Container(size=1280, px={"base": 16, "sm": 32}, py=40,
                         children=dmc.Stack(gap=48, children=[b for b in blocs if b is not None]))
