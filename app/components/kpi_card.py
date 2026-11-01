"""Carte KPI retournable (DESIGN_SYSTEM.md §6.2) — composant signature.

Recto épuré (demande du propriétaire) : pastille d'icône + libellé, valeur, UNE variation,
mini-courbe avec ses années de début et de fin.
Verso : « Comment le lire », ligne leader mise en avant, « Pour l'assureur » ;
la source s'affiche en infobulle de la carte (elle figure aussi sous chaque graphique).
Rotation : survol (pointeur fin), focus + Entrée / Espace, toucher (classe `on`, app/assets/app.js).
`vedette=True` : carte foncée qui ouvre la rangée (le chiffre principal de la scène).
"""

from __future__ import annotations

import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

from app.components.format import NA

CLASSE_SENS = {"defavorable": "pill-defavorable", "favorable": "pill-favorable",
               "neutre": "pill-neutre"}
ANNEES_SPARK = ("2019", "2025")


def sparkline(valeurs: list, hauteur: int = 30, annees=ANNEES_SPARK) -> html.Div:
    """Mini-courbe remplie, neutre ; pastille rouge sur le dernier point ; années aux bornes."""
    vals = [v for v in valeurs if v is not None and v == v]
    if len(vals) < 2:
        return html.Div(className="kpi-spark")
    lo, hi = min(vals), max(vals)
    # Recharts part de zéro : on décale la série pour qu'elle occupe toute la hauteur
    # (forme seule ; aucune valeur n'est lue sur la mini-courbe)
    base = lo - (hi - lo) * 0.15 if hi > lo else lo - 1
    traces = [v - base for v in vals]
    y = traces[-1] / max(traces)
    return html.Div(className="kpi-spark", children=[
        html.Div(className="spark-wrap", children=[
            dmc.Sparkline(data=traces, h=hauteur, color="var(--spark-ligne)",
                          curveType="monotone",
                          strokeWidth=1.75, fillOpacity=0.16, withGradient=False),
            # Recharts laisse ~2 px de marge haute et basse : pastille centrée sur le dernier point
            html.Span(className="spark-dot",
                      style={"top": f"{2 + (1 - y) * (hauteur - 4) - 4:.1f}px"}),
        ]),
        html.Div(className="kpi-spark-ans", children=[html.Span(annees[0]),
                                                       html.Span(annees[1])]),
    ])


def _pill(d: dict) -> html.Span:
    return html.Span(d["texte"], className=f"pill {CLASSE_SENS[d['sens']]}")


def kpi_card(kpi_id: str, label: str, icon: str, valeur: str, *, deltas: list[dict] = (),
             leader: tuple[str, list] | None = None, spark: list | None = None,
             lire: str, assureur: str, source: str, aria: str | None = None,
             indisponible: bool = False, compte: int | None = None,
             texte: bool = False, vedette: bool = False) -> html.Div:
    """`valeur` est déjà formatée (fmt_number / fmt_pct) ; `deltas` vient de format.delta.
    `compte` (entier) active le comptage animé au premier affichage (app.js).
    `texte=True` : valeur textuelle (nom, créneau) en corps réduit, sur 2 lignes au plus."""
    attrs = {"data-count": str(compte)} if compte is not None else {}
    na = indisponible or valeur == NA
    if na:
        deltas, spark = [], None
    valeur_node = (html.Div(className="kpi-na-bloc", children=[
        html.Span(NA, className="kpi-value kpi-na"),
        html.Span("Donnée indisponible", className="kpi-na-texte")])
        if na else html.Div(valeur, className="kpi-value kpi-value-texte" if texte
                            else "kpi-value", **attrs))

    recto = html.Div(className="kpi-face", children=[
        html.Div(className="kpi-top", children=[
            html.Span(DashIconify(icon=icon, width=18), className="kpi-icone"),
            html.Span(label, className="kpi-titre"),
            html.Span(DashIconify(icon="tabler:rotate-clockwise-2", width=14),
                      className="kpi-tourner", **{"aria-hidden": "true"}),
        ]),
        valeur_node,
        html.Div(className="kpi-deltas", children=[_pill(deltas[0])]) if deltas else None,
        sparkline(spark) if spark else None,
    ])
    verso = html.Div(className="kpi-face kpi-back", children=[
        html.Div("Comment le lire", className="kpi-back-title"),
        html.Div(lire, className="kpi-back-text kpi-clamp-3"),
        html.Div(className="kpi-back-text kpi-leader-verso", children=[
            DashIconify(icon=leader[0], width=14), html.Span(leader[1])]) if leader else None,
        html.Div("Pour l'assureur", className="kpi-back-title"),
        html.Div(assureur, className="kpi-back-text kpi-clamp-3"),
    ])
    morceaux = [f"{label} : {'donnée indisponible' if na else valeur}."]
    morceaux += [d["texte"].replace("▲", "hausse").replace("▼", "baisse") for d in deltas]
    if leader:
        morceaux.append("".join(x if isinstance(x, str) else str(x.children)
                                for x in leader[1]))
    morceaux.append(lire)
    morceaux.append(source)
    morceaux_source = source
    return html.Div(
        title=morceaux_source,
        id=kpi_id, className="kpi-flip kpi-vedette" if vedette else "kpi-flip", tabIndex=0,
        role="button", **{"aria-label": aria or " ".join(morceaux), "aria-pressed": "false"},
        children=html.Div(className="kpi-flip-inner", children=[recto, verso]))


def kpi_row(cartes: list) -> dmc.SimpleGrid:
    return dmc.SimpleGrid(cols={"base": 1, "sm": 2, "lg": 4}, spacing="lg", children=cartes)
