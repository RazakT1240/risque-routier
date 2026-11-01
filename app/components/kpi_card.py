"""Carte KPI retournable (DESIGN_SYSTEM.md §6.2) — composant signature.

Recto : libellé + icône, valeur, variations ▲▼, ligne leader, mini-courbe, indice de rotation.
Verso : « Comment le lire », « Pour l'assureur », source. Jamais de nouveau chiffre au verso.
Rotation : survol, focus clavier, Entrée/Espace et toucher (classe `on`, app/assets/app.js).
"""

from __future__ import annotations

import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

from app.components.format import NA

CLASSE_SENS = {"defavorable": "delta-hausse", "favorable": "delta-baisse",
               "neutre": "delta-neutre"}


def sparkline(valeurs: list, hauteur: int = 28) -> html.Div:
    """Mini-courbe neutre, dernier point en rouge gravité (pastille superposée)."""
    vals = [v for v in valeurs if v is not None]
    if len(vals) < 2:
        return html.Div(className="kpi-spark")
    lo, hi = min(vals), max(vals)
    dernier = vals[-1]
    y = 0.5 if hi == lo else (dernier - lo) / (hi - lo)
    return html.Div(className="kpi-spark spark-wrap", children=[
        dmc.Sparkline(data=vals, h=hauteur, color="var(--data-neutre)", curveType="monotone",
                      strokeWidth=1.5, fillOpacity=0, withGradient=False),
        html.Span(className="spark-dot", style={"top": f"calc({(1 - y) * 100:.1f}% - 3px)"}),
    ])


def kpi_card(kpi_id: str, label: str, icon: str, valeur: str, *, deltas: list[dict] = (),
             leader: tuple[str, list] | None = None, spark: list | None = None,
             lire: str, assureur: str, source: str, aria: str | None = None,
             indisponible: bool = False, compte: int | None = None,
             texte: bool = False) -> html.Div:
    """`valeur` est déjà formatée (fmt_number / fmt_pct) ; `deltas` vient de format.delta.
    `compte` (entier) active le comptage animé au premier affichage (app.js).
    `texte=True` : valeur textuelle (nom, créneau) en corps réduit, sur 2 lignes au plus."""
    attrs = {"data-count": str(compte)} if compte is not None else {}
    na = indisponible or valeur == NA
    valeur_node = (html.Div([html.Span(NA, className="kpi-value kpi-na"),
                             html.Span(" Donnée indisponible", className="kpi-na-texte")])
                   if na else html.Div(valeur, className="kpi-value kpi-value-texte" if texte
                                       else "kpi-value", **attrs))

    recto = html.Div(className="kpi-face", children=[
        html.Div(className="kpi-head", children=[
            DashIconify(icon=icon, width=16), html.Span(label, className="label")]),
        valeur_node,
        html.Div(className="kpi-deltas", children=[
            html.Span(d["texte"], className=CLASSE_SENS[d["sens"]]) for d in deltas]),
        html.Div(className="kpi-leader", children=[
            DashIconify(icon=leader[0], width=14), html.Span(leader[1])]) if leader else None,
        sparkline(spark) if spark else html.Div(className="kpi-spark"),
        html.Div(className="kpi-hint", **{"aria-hidden": "true"}, children=[
            DashIconify(icon="tabler:rotate-3d", width=12),
            html.Span("Survoler pour l'explication", className="hint-survol"),
            html.Span("Toucher pour l'explication", className="hint-toucher")]),
    ])
    verso = html.Div(className="kpi-face kpi-back", children=[
        html.Div("Comment le lire", className="kpi-back-title"),
        html.Div(lire, className="kpi-back-text"),
        html.Div("Pour l'assureur", className="kpi-back-title"),
        html.Div(assureur, className="kpi-back-text"),
        html.Div(source, className="caption", style={"marginTop": "auto"}),
    ])
    morceaux = [f"{label} : {'donnée indisponible' if na else valeur}."]
    morceaux += [d["texte"].replace("▲", "hausse").replace("▼", "baisse") for d in deltas]
    if leader:
        morceaux.append("".join(x if isinstance(x, str) else str(x.children)
                                for x in leader[1]))
    morceaux.append(lire)
    return html.Div(
        id=kpi_id, className="kpi-flip", tabIndex=0, role="button",
        **{"aria-label": aria or " ".join(morceaux), "aria-pressed": "false"},
        children=html.Div(className="kpi-flip-inner", children=[recto, verso]))


def kpi_row(cartes: list) -> dmc.SimpleGrid:
    return dmc.SimpleGrid(cols={"base": 1, "sm": 2, "lg": 4}, spacing="lg", children=cartes)
