"""Constructeurs de figures Plotly (DESIGN_SYSTEM.md §8) — une fonction par type de graphique.

Règles : tout en neutre, une seule couleur d'alerte (grav-tue) pour ce que le titre désigne (G10),
annotations directes plutôt que légende, aucun double axe Y (G11), formats français.
Chaque fonction reçoit `scheme` ('light' / 'dark') et lit les couleurs dans les tokens (G9).
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

from app.components.format import fmt_number, fmt_pct, fmt_ratio
from design.plotly_template import template_name
from design.tokens import FONT_SANS, FONT_SERIF, TRANSPARENT, tokens, transparence

HOVER_BASE = dict(hoverlabel=dict(namelength=-1))


def _base(fig: go.Figure, scheme: str, **layout) -> go.Figure:
    fig.update_layout(template=template_name(scheme), **HOVER_BASE, **layout)
    return fig


def _annot(t, x, y, texte, couleur=None, **kw):
    return dict(x=x, y=y, text=texte, showarrow=False, font=dict(
        family=FONT_SANS, size=12, color=couleur or t["text-secondary"]), **kw)


def bande_2020(fig, t, texte="Confinements", row=None, col=None):
    kw = dict(row=row, col=col) if row else {}
    fig.add_vrect(x0=2019.5, x1=2020.5, fillcolor=t["data-neutre-clair"], opacity=0.35,
                  line_width=0, layer="below", **kw)
    if texte:
        fig.add_annotation(**_annot(t, 2020, 1, texte, t["text-muted"], yref="paper",
                                    yanchor="bottom"))


def message_figure(texte: str, scheme: str) -> go.Figure:
    """Figure vide portant un message (effectif trop faible, donnée indisponible)."""
    t = tokens(scheme)
    fig = go.Figure()
    fig.add_annotation(**_annot(t, 0.5, 0.5, texte, t["text-muted"], xref="paper",
                                yref="paper"))
    return _base(fig, scheme, xaxis=dict(visible=False), yaxis=dict(visible=False))


# --- Scène 02 ------------------------------------------------------------

def lignes_base100(annees, series: dict[str, list], alerte: str, scheme: str) -> go.Figure:
    t = tokens(scheme)
    couleurs = iter([t["data-neutre"], t["data-neutre-clair"]])
    fig = go.Figure()
    for nom, vals in series.items():
        c = t["grav-tue"] if nom == alerte else next(couleurs)
        fig.add_trace(go.Scatter(
            x=annees, y=vals, name=nom, mode="lines+markers",
            line=dict(color=c, width=3 if nom == alerte else 2),
            marker=dict(size=[0] * (len(vals) - 1) + [8], color=c),
            hovertemplate=f"{nom} : %{{y:.0f}}<extra></extra>"))
        fig.add_annotation(**_annot(t, annees[-1], vals[-1],
                                    f"<b>{nom}</b> {fmt_number(vals[-1])}", c,
                                    xanchor="left", xshift=8))
    fig.add_hline(y=100, line=dict(color=t["border"], width=1, dash="dot"))
    bande_2020(fig, t)
    return _base(fig, scheme, hovermode="x unified", showlegend=False,
                 margin=dict(l=8, r=112, t=28, b=8),
                 xaxis=dict(dtick=1, range=[annees[0] - 0.3, annees[-1] + 0.3]),
                 yaxis=dict(title=None))


def barres_annuelles(annees, valeurs, scheme: str, alerte_derniere=True,
                     suffixe="") -> go.Figure:
    t = tokens(scheme)
    couleurs = [t["data-neutre"]] * len(valeurs)
    if alerte_derniere:
        couleurs[-1] = t["grav-tue"]
    fig = go.Figure(go.Bar(
        x=annees, y=valeurs, marker_color=couleurs, marker_line_width=0,
        marker_cornerradius=4, text=[fmt_number(v) + suffixe for v in valeurs],
        textposition="outside", cliponaxis=False, textfont=dict(color=t["text-primary"]),
        hovertemplate="%{x} : %{text}<extra></extra>"))
    bande_2020(fig, t, texte=None)
    return _base(fig, scheme, margin=dict(l=8, r=8, t=28, b=8), xaxis=dict(dtick=1),
                 yaxis=dict(showticklabels=False, showgrid=False), bargap=0.35)


# --- Scène 03 ------------------------------------------------------------

def barres_miroir(categories, part_gauche, part_droite, alerte: str, lib_g: str, lib_d: str,
                  scheme: str) -> go.Figure:
    t = tokens(scheme)
    cg = [t["grav-tue"] if c == alerte else t["data-neutre-clair"] for c in categories]
    cd = [t["grav-tue"] if c == alerte else t["data-neutre"] for c in categories]
    fig = go.Figure()
    fig.add_trace(go.Bar(y=categories, x=[-v for v in part_gauche], orientation="h", name=lib_g,
                         marker_color=cg, marker_line_width=0, marker_cornerradius=3,
                         text=[fmt_pct(v, 0) for v in part_gauche], textposition="outside",
                         cliponaxis=False, customdata=part_gauche,
                         hovertemplate=f"%{{y}} · {lib_g} : %{{customdata:.1f}} %<extra></extra>"))
    fig.add_trace(go.Bar(y=categories, x=part_droite, orientation="h", name=lib_d,
                         marker_color=cd, marker_line_width=0, marker_cornerradius=3,
                         text=[fmt_pct(v, 0) for v in part_droite], textposition="outside",
                         cliponaxis=False,
                         hovertemplate=f"%{{y}} · {lib_d} : %{{x:.1f}} %<extra></extra>"))
    borne = max(max(part_gauche), max(part_droite)) * 1.4
    ticks = [v for v in (-100, -50, 0, 50, 100) if abs(v) <= borne]
    fig.add_vline(x=0, line=dict(color=t["border"], width=1))
    i = list(categories).index(alerte)
    ecart = part_droite[i] - part_gauche[i]
    fig.add_annotation(**_annot(t, 0, alerte,
                                f"<b>écart {fmt_number(ecart, 0, signe=True)} pts</b>",
                                t["grav-tue"], yshift=-17))
    fig.add_annotation(**_annot(t, -borne, 1.02, f"← {lib_g}", t["text-secondary"],
                                xanchor="left", yref="paper", yanchor="bottom"))
    fig.add_annotation(**_annot(t, borne, 1.02, f"{lib_d} →", t["text-secondary"],
                                xanchor="right", yref="paper", yanchor="bottom"))
    return _base(fig, scheme, barmode="overlay", showlegend=False, bargap=0.3,
                 margin=dict(l=8, r=8, t=32, b=8),
                 xaxis=dict(range=[-borne, borne], tickvals=ticks, showline=False,
                            ticktext=[f"{abs(v)} %" for v in ticks], showgrid=True,
                            gridcolor=t["border"]),
                 yaxis=dict(autorange="reversed", showgrid=False))


def barres_categories(categories, valeurs, moyenne, scheme: str, alerte=None,
                      fmt=lambda v: fmt_number(v, 1), masques=None,
                      libelle_moyenne="Moyenne", titre_x: str | None = None) -> go.Figure:
    """Barres verticales ; `alerte` = catégorie en rouge (défaut : la plus haute) ;
    `masques` = catégories sous le seuil (grisées, sans valeur)."""
    t = tokens(scheme)
    masques = set(masques or [])
    visibles = [(c, v) for c, v in zip(categories, valeurs, strict=True) if c not in masques]
    if alerte is None and visibles:
        alerte = max(visibles, key=lambda cv: cv[1])[0]
    couleurs, textes, ys = [], [], []
    for c, v in zip(categories, valeurs, strict=True):
        masque = c in masques
        couleurs.append(t["seq-na"] if masque else
                        t["grav-tue"] if c == alerte else t["data-neutre"])
        textes.append("—" if masque else fmt(v))
        ys.append(0 if masque else v)
    fig = go.Figure(go.Bar(
        x=[str(c) for c in categories], y=ys, marker_color=couleurs, marker_line_width=0,
        marker_cornerradius=4, text=textes, textposition="outside", cliponaxis=False,
        textfont=dict(color=t["text-primary"]),
        hovertemplate="%{x} : %{customdata}<extra></extra>",
        customdata=["effectif trop faible" if c in masques else fmt(v)
                    for c, v in zip(categories, valeurs, strict=True)]))
    if moyenne is not None:
        fig.add_hline(y=moyenne, line=dict(color=t["text-secondary"], width=1, dash="dash"),
                      annotation_text=f"{libelle_moyenne} {fmt(moyenne)}",
                      annotation_position="top left",
                      annotation_font=dict(size=12, color=t["text-secondary"]))
    return _base(fig, scheme, margin=dict(l=8, r=8, t=28, b=8), bargap=0.3,
                 xaxis=dict(type="category", title=dict(text=titre_x, font=dict(size=12))),
                 yaxis=dict(showticklabels=False, showgrid=False, rangemode="tozero"))


# --- Scène 04 ------------------------------------------------------------

def courbes_age(classes, hommes, femmes, scheme: str, alerte_hommes=True) -> go.Figure:
    t = tokens(scheme)
    ch = t["grav-tue"] if alerte_hommes else t["text-primary"]
    fig = go.Figure()
    for nom, vals, c, w in (("Hommes", hommes, ch, 3), ("Femmes", femmes, t["data-neutre"], 2)):
        fig.add_trace(go.Scatter(x=classes, y=vals, name=nom, mode="lines", line=dict(
            color=c, width=w, shape="spline", smoothing=0.6), connectgaps=False,
            hovertemplate=f"{nom} · %{{x}} ans : %{{y:.1f}}<extra></extra>"))
        valides = [i for i, v in enumerate(vals) if v is not None and not np.isnan(v)]
        if not valides:
            continue
        fig.add_annotation(**_annot(t, classes[valides[-1]], vals[valides[-1]], f"<b>{nom}</b>",
                                    c, xanchor="left", xshift=6))
    valides = [(i, v) for i, v in enumerate(hommes) if v is not None and not np.isnan(v)]
    if valides:
        i, v = max(valides, key=lambda iv: iv[1])
        fig.add_annotation(x=classes[i], y=v,
                           text=f"Pic : {fmt_number(v, 0)} à {classes[i].replace('-', '–')} ans",
                           showarrow=True, arrowhead=0, arrowcolor=t["text-secondary"], ax=40,
                           ay=-28, font=dict(size=12, color=t["text-primary"]))
    return _base(fig, scheme, hovermode="x unified", showlegend=False,
                 margin=dict(l=8, r=70, t=28, b=8),
                 xaxis=dict(type="category", tickvals=classes[::2], tickangle=0,
                            ticktext=[c.split("-")[0] for c in classes[::2]],
                            title=dict(text="Âge (ans)", font=dict(size=12))),
                 yaxis=dict(rangemode="tozero"))


POSITIONS_ETIQUETTES = {"EDP": "bottom center", "Utilitaire": "top left", "Vélo": "top left",
                        "Bus, car, tram": "top right", "Poids lourd": "top right"}


def matrice_bulles(noms, x, y, tailles, alerte, scheme: str, lib_x: str, lib_y: str,
                   fmt_y=lambda v: fmt_pct(v)) -> go.Figure:
    t = tokens(scheme)
    mx, my = float(np.mean(x)), float(np.average(y))
    ref = max(tailles) or 1
    couleurs = [t["grav-tue"] if n == alerte else t["data-neutre"] for n in noms]
    fig = go.Figure(go.Scatter(
        x=x, y=y, mode="markers+text", text=noms,
        textposition=[POSITIONS_ETIQUETTES.get(n, "top center") for n in noms],
        textfont=dict(size=12, color=t["text-primary"]),
        marker=dict(size=[12 + 48 * (s / ref) ** 0.5 for s in tailles], color=couleurs,
                    opacity=0.85, line=dict(width=1, color=t["bg-surface"])),
        customdata=np.column_stack([tailles]),
        hovertemplate=(f"<b>%{{text}}</b><br>{lib_x} : %{{x:.1f}} %<br>{lib_y} : %{{y:.1f}} %"
                       "<br>Tués : %{customdata[0]:,.0f}<extra></extra>")))
    fig.add_vline(x=mx, line=dict(color=t["border"], width=1, dash="dot"))
    fig.add_hline(y=my, line=dict(color=t["border"], width=1, dash="dot"))
    # Noms des quadrants dans la marge haute / basse, hors de la zone des bulles
    for txt, xa, ya, xan, yan in (("↖ Rare et grave", 0, 1.0, "left", "bottom"),
                                  ("Fréquent et grave ↗", 1, 1.0, "right", "bottom"),
                                  ("↙ Rare et moins grave", 0, 0.0, "left", "top"),
                                  ("Fréquent et moins grave ↘", 1, 0.0, "right", "top")):
        fig.add_annotation(**_annot(t, xa, ya, txt, t["text-muted"], xref="paper", yref="paper",
                                    xanchor=xan, yanchor=yan, yshift=4 if ya else -22))
    graduations = [v for v in (0.5, 1, 2, 5, 10, 20, 50) if min(x) / 1.5 <= v <= max(x) * 1.5]
    return _base(fig, scheme, showlegend=False, margin=dict(l=8, r=8, t=28, b=40),
                 xaxis=dict(title=dict(text=lib_x, font=dict(size=12), standoff=24), type="log",
                            tickvals=graduations,
                            ticktext=[fmt_pct(v, 0 if v >= 1 else 1) for v in graduations],
                            showgrid=False),
                 yaxis=dict(title=dict(text=lib_y, font=dict(size=12)), ticksuffix=" %",
                            range=[0, max(y) * 1.2]))


# --- Scène 05 ------------------------------------------------------------

def classes_quantiles(valeurs: np.ndarray, n: int = 5) -> np.ndarray:
    v = valeurs[~np.isnan(valeurs)]
    return np.unique(np.quantile(v, np.linspace(0, 1, n + 1))) if len(v) else np.array([])


def contour_selection(geojson, dep: str, scheme: str) -> go.Choropleth:
    """Contour ambre d'un département (remplissage transparent), à superposer à une carte.
    Seule l'entité du département est transmise, pas tout le fond de carte."""
    t = tokens(scheme)
    entite = {"type": "FeatureCollection",
              "features": [f for f in geojson["features"] if f["properties"]["code"] == dep]}
    return go.Choropleth(
        geojson=entite, featureidkey="properties.code", locations=[dep], z=[0],
        colorscale=[[0, TRANSPARENT], [1, TRANSPARENT]], showscale=False,
        marker_line_color=t["accent"], marker_line_width=2.5, hoverinfo="skip")


def choroplethe(geojson, deps, noms, valeurs, scheme: str, unite: str,
                selection=None) -> tuple[go.Figure, list[float]]:
    t = tokens(scheme)
    seq = [t[f"seq-{i}"] for i in range(1, 6)]
    vals = np.array(valeurs, dtype=float)
    bornes = classes_quantiles(vals)
    rang = (-vals).argsort().argsort() + 1
    n_valides = int((~np.isnan(vals)).sum())
    fig = go.Figure()
    ok = ~np.isnan(vals)
    if ok.any():
        cls = np.clip(np.searchsorted(bornes, vals[ok], side="right") - 1, 0, len(bornes) - 2)
        k = max(len(bornes) - 1, 1)
        echelle = []
        for i in range(k):
            echelle += [[i / k, seq[i]], [(i + 1) / k, seq[i]]]
        fig.add_trace(go.Choropleth(
            geojson=geojson, featureidkey="properties.code",
            locations=np.array(deps)[ok], z=cls, zmin=0, zmax=k - 1 if k > 1 else 1,
            colorscale=echelle, showscale=False,
            marker_line_color=t["bg-surface"], marker_line_width=0.5,
            customdata=np.column_stack([np.array(noms)[ok], vals[ok], rang[ok]]),
            hovertemplate=("<b>%{customdata[0]}</b><br>%{customdata[1]:.1f} " + unite
                           + f"<br>Rang %{{customdata[2]}} / {n_valides}<extra></extra>")))
    if (~ok).any():
        fig.add_trace(go.Choropleth(
            geojson=geojson, featureidkey="properties.code", locations=np.array(deps)[~ok],
            z=[0] * int((~ok).sum()), colorscale=[[0, t["seq-na"]], [1, t["seq-na"]]],
            showscale=False, marker_line_color=t["bg-surface"], marker_line_width=0.5,
            customdata=np.array(noms)[~ok],
            hovertemplate="<b>%{customdata}</b><br>Effectif trop faible<extra></extra>"))
    if selection:
        fig.add_trace(contour_selection(geojson, selection, scheme))
    fig.update_geos(fitbounds="locations", visible=False, projection_type="conic conformal",
                    bgcolor=TRANSPARENT)
    _base(fig, scheme, margin=dict(l=0, r=0, t=0, b=0), dragmode=False)
    return fig, list(bornes)


def heatmap_jour_heure(z, masque, jours, scheme: str, fmt_hover: str,
                       cadre_weekend=True) -> go.Figure:
    t = tokens(scheme)
    seq = [t[f"seq-{i}"] for i in range(1, 6)]
    zz = np.array(z, dtype=float)
    zz[np.array(masque, dtype=bool)] = np.nan
    fig = go.Figure(go.Heatmap(
        z=zz, x=list(range(24)), y=jours, xgap=2, ygap=2,
        colorscale=[[i / 4, c] for i, c in enumerate(seq)], showscale=False,
        hovertemplate="%{y} · %{x} h : " + fmt_hover + "<extra></extra>", hoverongaps=False))
    # Cellules masquées (sous le seuil) : fond seq-na
    fig.add_trace(go.Heatmap(
        z=np.where(np.isnan(zz), 0, np.nan), x=list(range(24)), y=jours, xgap=2, ygap=2,
        colorscale=[[0, t["seq-na"]], [1, t["seq-na"]]], showscale=False,
        hovertemplate="%{y} · %{x} h : effectif trop faible<extra></extra>", hoverongaps=False))
    if cadre_weekend:
        for jour in ("Samedi", "Dimanche"):
            i = jours.index(jour)
            fig.add_shape(type="rect", x0=-0.5, x1=5.5, y0=i - 0.5, y1=i + 0.5,
                          line=dict(color=t["text-primary"], width=1.5))
        fig.add_annotation(**_annot(t, 2.5, 1.0, "Nuits de week-end", t["text-primary"],
                                    yref="paper", yanchor="bottom"))
    return _base(fig, scheme, margin=dict(l=8, r=8, t=24, b=8),
                 xaxis=dict(dtick=2, ticksuffix=" h", showline=False, ticks=""),
                 yaxis=dict(autorange="reversed", showgrid=False))


def barres_heure(heures, valeurs, scheme: str, fmt=lambda v: fmt_number(v)) -> go.Figure:
    """Valeurs NaN = sous le seuil : barre grisée basse, « effectif trop faible » au survol."""
    t = tokens(scheme)
    vals = np.array(valeurs, dtype=float)
    imax = int(np.nanargmax(vals)) if np.isfinite(vals).any() else -1
    plancher = np.nanmax(vals) * 0.04 if np.isfinite(vals).any() else 0
    fig = go.Figure(go.Bar(
        x=heures, y=np.where(np.isnan(vals), plancher, vals), marker_line_width=0,
        marker_cornerradius=2,
        marker_color=[t["seq-na"] if np.isnan(v) else t["grav-tue"] if i == imax
                      else t["data-neutre"] for i, v in enumerate(vals)],
        customdata=["effectif trop faible" if np.isnan(v) else fmt(v) for v in vals],
        hovertemplate="%{x} h : %{customdata}<extra></extra>"))
    return _base(fig, scheme, margin=dict(l=8, r=8, t=8, b=8), bargap=0.15,
                 xaxis=dict(dtick=3, ticksuffix=" h"), yaxis=dict(showticklabels=False))


def barres_classees(noms, valeurs, scheme: str, unite: str, n: int = 12) -> go.Figure:
    """Remplace la carte sous 768 px : départements classés (n premiers)."""
    t = tokens(scheme)
    paires = sorted([(v, nm) for nm, v in zip(noms, valeurs, strict=True) if not np.isnan(v)],
                    reverse=True)[:n]
    fig = go.Figure(go.Bar(
        y=[nm for _, nm in paires], x=[v for v, _ in paires], orientation="h",
        marker_color=[t["grav-tue"]] + [t["data-neutre"]] * (len(paires) - 1),
        marker_line_width=0, text=[fmt_number(v, 1) for v, _ in paires],
        textposition="outside", cliponaxis=False,
        hovertemplate="%{y} : %{x:.1f} " + unite + "<extra></extra>"))
    return _base(fig, scheme, margin=dict(l=8, r=40, t=8, b=8),
                 yaxis=dict(autorange="reversed", showgrid=False),
                 xaxis=dict(showticklabels=False, showgrid=False))


def risques_relatifs(libelles, rr, bas, haut, scheme: str, alerte=None) -> go.Figure:
    t = tokens(scheme)
    couleurs = [t["grav-tue"] if lb == alerte else t["data-neutre"] for lb in libelles]
    fig = go.Figure(go.Scatter(
        x=rr, y=libelles, mode="markers", orientation="h",
        marker=dict(size=12, color=couleurs, symbol="square"),
        error_x=dict(type="data", array=[h - r for r, h in zip(rr, haut, strict=True)],
                     arrayminus=[r - b for r, b in zip(rr, bas, strict=True)],
                     thickness=1.25, width=4, color=t["text-secondary"]),
        customdata=np.column_stack([bas, haut]),
        hovertemplate=("%{y} : × %{x:.2f}<br>IC 95 % : %{customdata[0]:.2f} – "
                       "%{customdata[1]:.2f}<extra></extra>")))
    fig.add_vline(x=1, line=dict(color=t["text-secondary"], width=1))
    for lb, r, h in zip(libelles, rr, haut, strict=True):
        fig.add_annotation(**_annot(t, h, lb, fmt_ratio(r), t["text-primary"], xanchor="left",
                                    xshift=8))
    lo, hi = min(bas), max(haut)
    marge = (hi - lo) * 0.35 + 0.02
    return _base(fig, scheme, margin=dict(l=8, r=8, t=8, b=8), showlegend=False,
                 xaxis=dict(range=[min(lo, 1) - marge, max(hi, 1) + marge * 1.6],
                            tickprefix="× ", showgrid=True, gridcolor=t["border"]),
                 yaxis=dict(autorange="reversed", showgrid=False))


# --- Scène 06 ------------------------------------------------------------

@lru_cache(maxsize=2)
def _template_json(scheme: str) -> dict:
    return pio.templates[template_name(scheme)].to_plotly_json()


def petits_multiples(annees, series: dict[str, list], alerte: str, scheme: str,
                     cols: int = 3) -> dict:
    """Une mini-courbe par série, même échelle Y. Construite directement en dictionnaire
    (sans validation Plotly objet par objet : 9 sous-graphiques en quelques ms)."""
    t = tokens(scheme)
    noms = list(series)
    rows = int(np.ceil(len(noms) / cols))
    vmax = max(max(v for v in s if v is not None) for s in series.values())
    haut_y = vmax * 1.22
    gx, gy = 0.05, 0.12
    largeur, hauteur = (1 - gx * (cols - 1)) / cols, (1 - gy * (rows - 1)) / rows
    data, shapes, annotations = [], [], []
    layout = {"template": _template_json(scheme), "showlegend": False,
              "margin": {"l": 8, "r": 8, "t": 28, "b": 8},
              "hoverlabel": {"namelength": -1}}
    for k, nom in enumerate(noms):
        r, c = k // cols, k % cols
        suffixe = "" if k == 0 else str(k + 1)
        x0 = c * (largeur + gx)
        y1 = 1 - r * (hauteur + gy)
        xa, ya = f"x{suffixe}", f"y{suffixe}"
        layout[f"xaxis{suffixe}"] = {"domain": [max(x0, 0), min(x0 + largeur, 1)], "anchor": ya,
                                     "dtick": 3, "tickfont": {"size": 10},
                                     "showticklabels": r == rows - 1}
        layout[f"yaxis{suffixe}"] = {"domain": [max(y1 - hauteur, 0), min(y1, 1)], "anchor": xa,
                                     "range": [0, haut_y], "nticks": 4, "tickfont": {"size": 10},
                                     "showticklabels": c == 0}
        vals = series[nom]
        coul = t["grav-tue"] if nom == alerte else t["data-neutre"]
        data.append({"type": "scatter", "x": list(annees), "y": vals, "mode": "lines",
                     "line": {"color": coul, "width": 2}, "xaxis": xa, "yaxis": ya,
                     "hovertemplate": f"{nom} · %{{x}} : %{{y:.0f}}<extra></extra>"})
        data.append({"type": "scatter", "x": [annees[-1]], "y": [vals[-1]],
                     "mode": "markers+text", "marker": {"color": coul, "size": 6},
                     "text": [fmt_number(vals[-1])], "textposition": "top left",
                     "textfont": {"size": 11, "color": coul}, "hoverinfo": "skip",
                     "xaxis": xa, "yaxis": ya})
        shapes.append({"type": "line", "x0": annees[0], "x1": annees[-1], "y0": 100, "y1": 100,
                       "xref": xa, "yref": ya,
                       "line": {"color": t["border"], "width": 1, "dash": "dot"}})
        shapes.append({"type": "rect", "x0": 2019.5, "x1": 2020.5, "y0": 0, "y1": haut_y,
                       "xref": xa, "yref": ya, "fillcolor": t["data-neutre-clair"],
                       "opacity": 0.35, "line": {"width": 0}, "layer": "below"})
        annotations.append({"text": nom, "x": x0 + largeur / 2, "y": y1, "xref": "paper",
                            "yref": "paper", "yanchor": "bottom", "showarrow": False,
                            "font": {"family": FONT_SERIF, "size": 14,
                                     "color": t["text-primary"]}})
    layout.update(shapes=shapes, annotations=annotations)
    return {"data": data, "layout": layout}


def pareto(segments, parts, cumul, seuil, scheme: str) -> go.Figure:
    """Barres = part de chaque segment, ligne = part cumulée : même axe en % (pas de double axe)."""
    t = tokens(scheme)
    n80 = next((i for i, c in enumerate(cumul) if c >= seuil), len(cumul) - 1)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=segments, y=parts, marker_line_width=0, marker_cornerradius=3,
        marker_color=[t["data-neutre"] if i <= n80 else t["data-neutre-clair"]
                      for i in range(len(parts))],
        text=[fmt_pct(p, 0) for p in parts], textposition="outside", cliponaxis=False,
        textfont=dict(size=11, color=t["text-secondary"]),
        hovertemplate="%{x} : %{y:.1f} % du poids<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=segments, y=cumul, mode="lines+markers", line=dict(color=t["text-primary"], width=2),
        marker=dict(size=5), hovertemplate="Cumul : %{y:.1f} %<extra></extra>"))
    fig.add_hline(y=seuil, line=dict(color=t["text-secondary"], width=1.5, dash="dash"))
    fig.add_annotation(**_annot(t, n80, seuil,
                                f"<b>{n80 + 1} segments = {fmt_pct(cumul[n80], 0)}</b>",
                                t["text-primary"], xanchor="left", yanchor="top", xshift=10,
                                yshift=-6))
    return _base(fig, scheme, showlegend=False, margin=dict(l=8, r=8, t=16, b=8),
                 xaxis=dict(tickangle=-35, tickfont=dict(size=11)),
                 yaxis=dict(range=[0, 105], ticksuffix=" %"))


# --- Graphiques ajoutés (refonte visuelle) -----------------------------------

def donut(libelles, valeurs, couleurs, centre: str, sous_centre: str, scheme: str) -> go.Figure:
    """Anneau de répartition, 3 parts au plus (G11), légende directe en bas."""
    if len(valeurs) > 3:
        raise ValueError("Un anneau de répartition ne peut pas avoir plus de 3 parts (G11).")
    t = tokens(scheme)
    total = sum(valeurs)
    fig = go.Figure(go.Pie(
        labels=libelles, values=valeurs, hole=0.68, sort=False, direction="clockwise",
        marker=dict(colors=couleurs, line=dict(color=t["bg-surface"], width=3)),
        textinfo="none", customdata=[fmt_pct(v / total * 100, 1) for v in valeurs],
        hovertemplate="%{label} : %{value:,.0f} (%{customdata})<extra></extra>"))
    fig.add_annotation(**_annot(t, 0.5, 0.56, f"<b>{centre}</b>", t["text-primary"],
                                xref="paper", yref="paper"))
    fig.layout.annotations[-1].font.update(size=26, family=FONT_SANS)
    fig.add_annotation(**_annot(t, 0.5, 0.42, sous_centre, t["text-secondary"], xref="paper",
                                yref="paper"))
    return _base(fig, scheme, showlegend=True, margin=dict(l=8, r=8, t=8, b=8),
                 legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center",
                             font=dict(size=12, color=t["text-secondary"])))


def anneau_jauge(part: float, libelle: str, scheme: str, alerte: bool = True) -> go.Figure:
    """Jauge en anneau : une part (0–100 %) sur fond neutre."""
    t = tokens(scheme)
    coul = t["grav-tue"] if alerte else t["data-neutre"]
    fig = go.Figure(go.Pie(
        values=[part, 100 - part], hole=0.78, sort=False, direction="clockwise", rotation=0,
        marker=dict(colors=[coul, t["seq-na"]], line=dict(width=0)), textinfo="none",
        hoverinfo="skip"))
    fig.add_annotation(**_annot(t, 0.5, 0.55, f"<b>{fmt_pct(part, 0)}</b>", t["text-primary"],
                                xref="paper", yref="paper"))
    fig.layout.annotations[-1].font.update(size=30)
    fig.add_annotation(**_annot(t, 0.5, 0.38, libelle, t["text-secondary"], xref="paper",
                                yref="paper"))
    return _base(fig, scheme, showlegend=False, margin=dict(l=4, r=4, t=4, b=4))


def courbe_annotee(annees, valeurs, scheme: str, fmt=lambda v: fmt_number(v, 1),
                   plus_est_mauvais: bool | None = True, unite: str = "",
                   points: bool = False) -> go.Figure:
    """Évolution année par année : chaque point étiqueté, creux et pic en pastilles,
    variation annuelle sous l'axe (couleur selon le sens pour l'assureur)."""
    t = tokens(scheme)
    vals = [None if v is None or v != v else v for v in valeurs]
    ok = [(a, v) for a, v in zip(annees, vals, strict=True) if v is not None]
    fig = go.Figure(go.Scatter(
        x=annees, y=vals, mode="lines+markers+text",
        line=dict(color=t["text-primary"], width=2.5, shape="spline", smoothing=0.5),
        marker=dict(size=8, color=t["bg-surface"], line=dict(color=t["text-primary"], width=2)),
        text=[fmt(v) if v is not None else "" for v in vals], textposition="top center",
        textfont=dict(size=12, color=t["text-secondary"]), cliponaxis=False,
        hovertemplate="%{x} : %{text}" + (f" {unite}" if unite else "") + "<extra></extra>",
        connectgaps=False))
    if ok:
        bas, haut = min(ok, key=lambda x: x[1]), max(ok, key=lambda x: x[1])
        for (a, v), txt, coul in ((bas, "Creux", t["data-neutre"]), (haut, "Pic", t["grav-tue"])):
            fig.add_annotation(x=a, y=v, text=f"<b>{txt}</b>", showarrow=False, yshift=-22,
                               font=dict(size=11, color=t["bg-surface"]), bgcolor=coul,
                               borderpad=3)
    for i in range(1, len(vals)):
        if vals[i] is None or vals[i - 1] in (None, 0):
            continue
        var = vals[i] - vals[i - 1] if points else (vals[i] / vals[i - 1] - 1) * 100
        if plus_est_mauvais is None:
            coul = t["text-muted"]
        else:
            coul = t["delta-hausse"] if (var > 0) == plus_est_mauvais else t["delta-baisse"]
        fig.add_annotation(x=annees[i], y=0, yref="paper", yshift=-34, showarrow=False,
                           text=(f"{fmt_number(var, 1, signe=True)} pt" if points
                                 else fmt_pct(var, 1, signe=True)),
                           font=dict(size=10, color=coul))
    vv = [v for _, v in ok] or [0, 1]
    marge = (max(vv) - min(vv)) * 0.35 or max(vv) * 0.1 or 1
    return _base(fig, scheme, showlegend=False, margin=dict(l=8, r=8, t=24, b=40),
                 xaxis=dict(dtick=1, range=[annees[0] - 0.4, annees[-1] + 0.4]),
                 yaxis=dict(showticklabels=False, showgrid=False,
                            range=[min(vv) - marge, max(vv) + marge]))


def boites(stats: list[dict], scheme: str, alerte: str | None = None,
           titre_y: str = "Âge (ans)") -> go.Figure:
    """Boîtes à moustaches à partir de statistiques précalculées (q1, médiane, q3, bas, haut)."""
    t = tokens(scheme)
    fig = go.Figure()
    for s in stats:
        coul = t["grav-tue"] if s["nom"] == alerte else t["data-neutre"]
        fig.add_trace(go.Box(
            name=s["nom"], x=[s["nom"]], q1=[s["q1"]], median=[s["mediane"]], q3=[s["q3"]],
            lowerfence=[s["bas"]], upperfence=[s["haut"]], mean=[s["moyenne"]], boxmean=True,
            marker_color=coul, line=dict(color=coul, width=1.5), fillcolor=coul, opacity=0.85,
            whiskerwidth=0.4, width=0.55,
            hovertemplate=(f"<b>{s['nom']}</b><br>Médiane : {fmt_number(s['mediane'], 0)} ans"
                           f"<br>Moitié centrale : {fmt_number(s['q1'], 0)} – "
                           f"{fmt_number(s['q3'], 0)} ans<br>Effectif : {fmt_number(s['n'])}"
                           "<extra></extra>")))
        fig.add_annotation(**_annot(t, s["nom"], s["mediane"], fmt_number(s["mediane"], 0),
                                    t["text-primary"], xshift=26))
    return _base(fig, scheme, showlegend=False, margin=dict(l=8, r=8, t=12, b=8),
                 yaxis=dict(title=dict(text=titre_y, font=dict(size=12)), rangemode="tozero"),
                 xaxis=dict(showline=False))


def boites_annuelles(annees, valeurs_par_annee: dict, scheme: str, unite: str,
                     selection: dict | None = None) -> go.Figure:
    """Dispersion d'un taux entre départements, une boîte par année, points visibles ;
    `selection` = {année: valeur} du département filtré (pastille ambre)."""
    t = tokens(scheme)
    fig = go.Figure()
    for a in annees:
        vals = [v for v in valeurs_par_annee.get(a, []) if v == v]
        fig.add_trace(go.Box(
            y=vals, name=str(a), boxpoints="all", jitter=0.45, pointpos=0,
            marker=dict(size=4, color=t["data-neutre-clair"], opacity=0.8),
            line=dict(color=t["data-neutre"], width=1.5), fillcolor=t["bg-subtle"],
            whiskerwidth=0.4, hoveron="boxes",
            hovertemplate=f"{a}<br>Médiane : %{{median:.1f}} {unite}<extra></extra>"))
    if selection:
        xs = [a for a in annees if selection.get(a) is not None and selection[a] == selection[a]]
        fig.add_trace(go.Scatter(
            x=[str(a) for a in xs], y=[selection[a] for a in xs], mode="lines+markers",
            line=dict(color=t["accent"], width=2),
            marker=dict(size=9, color=t["accent"], line=dict(color=t["bg-surface"], width=2)),
            name="Département filtré",
            hovertemplate="%{x} : %{y:.1f} " + unite + "<extra>Département filtré</extra>"))
    return _base(fig, scheme, showlegend=False, margin=dict(l=8, r=8, t=12, b=8),
                 yaxis=dict(title=dict(text=unite, font=dict(size=12)), rangemode="tozero"))


def matrice(lignes, colonnes, z, masque, scheme: str, fmt=lambda v: fmt_number(v, 1),
            titre_x: str | None = None, survol: str = "", annoter: bool = True) -> go.Figure:
    """Matrice annotée (valeur dans chaque case), échelle séquentielle ; cases masquées grisées."""
    t = tokens(scheme)
    seq = [t[f"seq-{i}"] for i in range(1, 6)]
    zz = np.array(z, dtype=float)
    zz[np.array(masque, dtype=bool)] = np.nan
    vmax = np.nanmax(zz) if np.isfinite(zz).any() else 1
    fig = go.Figure(go.Heatmap(
        z=zz, x=colonnes, y=lignes, xgap=3, ygap=3, showscale=False,
        colorscale=[[i / 4, c] for i, c in enumerate(seq)], hoverongaps=False,
        hovertemplate="%{y} · %{x} : %{z:.1f}" + survol + "<extra></extra>"))
    fig.add_trace(go.Heatmap(
        z=np.where(np.isnan(zz), 0, np.nan), x=colonnes, y=lignes, xgap=3, ygap=3,
        colorscale=[[0, t["seq-na"]], [1, t["seq-na"]]], showscale=False, hoverongaps=False,
        hovertemplate="%{y} · %{x} : effectif trop faible<extra></extra>"))
    for i, ligne in enumerate(lignes):
        for j, col in enumerate(colonnes):
            v = zz[i][j]
            if np.isnan(v) or not annoter:
                continue
            # Cases foncées -> texte clair ; cases vives du mode sombre -> texte foncé
            # Échelle séquentielle : sombre -> vive en mode sombre, claire -> foncée en clair
            if scheme == "dark":
                coul = t["bg-page"] if v > vmax * 0.85 else t["text-primary"]
            else:
                coul = t["on-image"] if v > vmax * 0.55 else t["text-primary"]
            fig.add_annotation(x=col, y=ligne, text=fmt(v), showarrow=False,
                               font=dict(size=12, color=coul))
    return _base(fig, scheme, margin=dict(l=8, r=8, t=8, b=8),
                 xaxis=dict(side="top", showline=False, ticks="",
                            title=dict(text=titre_x, font=dict(size=12))),
                 yaxis=dict(autorange="reversed", showgrid=False, ticks=""))


def barres_100(annees, parts: dict[str, list], couleurs: dict[str, str], scheme: str) -> go.Figure:
    """Barres empilées à 100 % par année ; étiquettes directes à droite (pas de légende)."""
    t = tokens(scheme)
    fig = go.Figure()
    for nom, vals in parts.items():
        fig.add_trace(go.Bar(
            x=annees, y=vals, name=nom, marker_color=couleurs[nom], marker_line_width=0,
            text=[fmt_pct(v, 0) if v >= 6 else "" for v in vals], textposition="inside",
            insidetextanchor="middle", textfont=dict(size=11, color=t["on-image"]),
            hovertemplate=f"{nom} · %{{x}} : %{{y:.1f}} %<extra></extra>"))
    # Libellés hors du tracé, à droite, espacés d'au moins 7 points pour ne pas se chevaucher
    cumul, positions = 0, []
    for nom, vals in parts.items():
        positions.append([nom, cumul + vals[-1] / 2])
        cumul += vals[-1]
    for i in range(1, len(positions)):
        positions[i][1] = max(positions[i][1], positions[i - 1][1] + 7)
    for nom, y in positions:
        fig.add_annotation(**_annot(t, 1, min(y, 100), f"<b>{nom}</b>", couleurs[nom],
                                    xref="paper", xanchor="left", xshift=8))
    return _base(fig, scheme, barmode="stack", bargap=0.28, showlegend=False,
                 margin=dict(l=8, r=150, t=8, b=8), xaxis=dict(dtick=1),
                 yaxis=dict(range=[0, 100], ticksuffix=" %", showgrid=False))


# --- Jauges, rose des mois, radar, pente --------------------------------------

def jauge(valeur: float, reference: float | None, vmin: float, vmax: float, scheme: str,
          suffixe: str = "", lib_ref: str = "", decimals: int = 1,
          plus_est_mauvais: bool = True) -> go.Figure:
    """Jauge semi-circulaire : aiguille pleine jusqu'à la valeur, repère de référence."""
    t = tokens(scheme)
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta" if reference is not None else "gauge+number",
        value=valeur,
        number=dict(valueformat=f".{decimals}f", suffix=suffixe,
                    font=dict(family=FONT_SANS, size=40, color=t["text-primary"])),
        delta=dict(reference=reference, valueformat=f".{decimals}f", relative=False,
                   increasing=dict(color=t["delta-hausse"] if plus_est_mauvais
                                   else t["delta-baisse"], symbol="▲ "),
                   decreasing=dict(color=t["delta-baisse"] if plus_est_mauvais
                                   else t["delta-hausse"], symbol="▼ "),
                   font=dict(size=14)) if reference is not None else None,
        gauge=dict(
            shape="angular", axis=dict(range=[vmin, vmax], tickwidth=1, tickcolor=t["border"],
                                       tickfont=dict(size=11, color=t["text-muted"]),
                                       nticks=6),
            bar=dict(color=t["grav-tue"], thickness=0.28), bgcolor=t["seq-na"], borderwidth=0,
            threshold=dict(line=dict(color=t["text-primary"], width=3), thickness=0.85,
                           value=reference) if reference is not None else None)))
    if reference is not None and lib_ref:
        fig.add_annotation(**_annot(t, 0.5, -0.08, f"Repère noir : {lib_ref}", t["text-muted"],
                                    xref="paper", yref="paper"))
    return _base(fig, scheme, margin=dict(l=36, r=40, t=16, b=28))


MOIS_COURTS = ["Janv.", "Févr.", "Mars", "Avr.", "Mai", "Juin", "Juil.", "Août", "Sept.", "Oct.",
               "Nov.", "Déc."]


def rose_mois(valeurs: list, scheme: str, unite: str = "tués") -> go.Figure:
    """Diagramme radial : un secteur par mois ; le mois le plus lourd en rouge."""
    t = tokens(scheme)
    imax = int(np.argmax(valeurs))
    fig = go.Figure(go.Barpolar(
        r=valeurs, theta=MOIS_COURTS,
        marker=dict(color=[t["grav-tue"] if i == imax else t["data-neutre"]
                           for i in range(12)], line=dict(color=t["bg-surface"], width=2)),
        hovertemplate="%{theta} : %{r:,.0f} " + unite + "<extra></extra>"))
    fig.update_layout(polar=dict(
        bgcolor=TRANSPARENT, hole=0.18,
        radialaxis=dict(showticklabels=False, showline=False, gridcolor=t["border"], ticks=""),
        angularaxis=dict(direction="clockwise", rotation=90, gridcolor=t["border"],
                         linecolor=t["border"], tickfont=dict(size=12, color=t["text-secondary"]))))
    return _base(fig, scheme, showlegend=False, margin=dict(l=40, r=40, t=24, b=24))


def radar(axes: list[str], series: dict[str, list], couleurs: dict[str, str],
          scheme: str) -> go.Figure:
    """Radar de profils (même unité sur tous les axes) ; remplissage léger, légende en bas."""
    t = tokens(scheme)
    fig = go.Figure()
    for nom, vals in series.items():
        fig.add_trace(go.Scatterpolar(
            r=vals + vals[:1], theta=axes + axes[:1], name=nom, mode="lines+markers",
            line=dict(color=couleurs[nom], width=2.5), marker=dict(size=6),
            fill="toself", fillcolor=transparence(couleurs[nom], 0.14),
            hovertemplate=f"{nom} · %{{theta}} : %{{r:.1f}} %<extra></extra>"))
    fig.update_layout(polar=dict(
        bgcolor=TRANSPARENT,
        radialaxis=dict(ticksuffix=" %", tickfont=dict(size=9, color=t["text-muted"]),
                        gridcolor=t["border"], linecolor=t["border"], angle=90, nticks=4,
                        tickangle=90, rangemode="tozero"),
        angularaxis=dict(gridcolor=t["border"], linecolor=t["border"],
                         tickfont=dict(size=12, color=t["text-primary"]))))
    return _base(fig, scheme, showlegend=True, margin=dict(l=48, r=48, t=24, b=24),
                 legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center"))


def pente(noms: list[str], debut: list, fin: list, annees: tuple[int, int], scheme: str,
          alerte: str | None = None, fmt=lambda v: fmt_number(v)) -> go.Figure:
    """Graphique de pente : une ligne par catégorie entre deux années, étiquettes aux deux bouts."""
    t = tokens(scheme)
    fig = go.Figure()
    for nom, a, b in zip(noms, debut, fin, strict=True):
        coul = t["grav-tue"] if nom == alerte else t["data-neutre"]
        larg = 3 if nom == alerte else 1.75
        fig.add_trace(go.Scatter(
            x=[str(annees[0]), str(annees[1])], y=[a, b], mode="lines+markers",
            line=dict(color=coul, width=larg), marker=dict(size=7, color=coul),
            hovertemplate=f"{nom} · %{{x}} : %{{y:,.0f}}<extra></extra>"))
        # Annotations positionnées par indice de catégorie (0, 1) : Plotly lirait « 2019 »
        # comme une position numérique
        fig.add_annotation(**_annot(t, 1, b, f"<b>{nom}</b> {fmt(b)}", coul,
                                    xanchor="left", xshift=10))
        fig.add_annotation(**_annot(t, 0, a, fmt(a), t["text-muted"],
                                    xanchor="right", xshift=-10))
    return _base(fig, scheme, showlegend=False, margin=dict(l=60, r=170, t=16, b=8),
                 xaxis=dict(type="category", showgrid=False, showline=False, ticks="",
                            range=[-0.08, 1.08], autorange=False),
                 yaxis=dict(type="log", showticklabels=False, showgrid=False))


# --- Sankey, entonnoir, pyramide, treemap (inspirés des dépôts de référence) ----

def sankey(sources: list[str], milieux: list[str], fins: list[str], flux: list[tuple],
           couleurs_fin: dict[str, str], scheme: str) -> go.Figure:
    """Flux à trois étages ; `flux` = [(source, milieu, fin, valeur)]. Les liens prennent la
    couleur de l'étage final (gravité), en transparence ; les nœuds restent neutres."""
    t = tokens(scheme)
    noeuds = sources + milieux + fins
    idx = {n: i for i, n in enumerate(noeuds)}
    s1, m1, v1, c1 = [], [], [], []
    agg_sm: dict[tuple, float] = {}
    for s, m, _f, v in flux:
        agg_sm[(s, m)] = agg_sm.get((s, m), 0) + v
    for (s, m), v in agg_sm.items():
        s1.append(idx[s])
        m1.append(idx[m])
        v1.append(v)
        c1.append(transparence(t["data-neutre"], 0.25))
    agg_mf: dict[tuple, float] = {}
    for _, m, f, v in flux:
        agg_mf[(m, f)] = agg_mf.get((m, f), 0) + v
    for (m, f), v in agg_mf.items():
        s1.append(idx[m])
        m1.append(idx[f])
        v1.append(v)
        c1.append(transparence(couleurs_fin[f], 0.45))
    couleurs_noeuds = ([t["data-neutre"]] * len(sources) + [t["text-secondary"]] * len(milieux)
                       + [couleurs_fin[f] for f in fins])
    fig = go.Figure(go.Sankey(
        arrangement="snap", valueformat=",.0f",
        node=dict(label=noeuds, pad=14, thickness=14, color=couleurs_noeuds,
                  line=dict(width=0),
                  hovertemplate="<b>%{label}</b><br>%{value:,.0f}<extra></extra>"),
        link=dict(source=s1, target=m1, value=v1, color=c1,
                  hovertemplate="%{source.label} → %{target.label} : %{value:,.0f}"
                                "<extra></extra>")))
    fig.update_traces(textfont=dict(family=FONT_SANS, size=12, color=t["text-primary"]),
                      selector=dict(type="sankey"))
    return _base(fig, scheme, margin=dict(l=8, r=8, t=8, b=8))


def entonnoir(etapes: list[str], valeurs: list[float], scheme: str) -> go.Figure:
    """Entonnoir de gravité : chaque étape en neutre, la dernière (les tués) en rouge ;
    part de l'étape précédente affichée à côté de la valeur."""
    t = tokens(scheme)
    couleurs = [t["data-neutre-clair"], t["data-neutre"], t["grav-hospi"], t["grav-tue"]]
    textes = [fmt_number(valeurs[0])] + [
        f"{fmt_number(v)}  ·  {fmt_pct(v / p * 100, 1)} de l'étape précédente"
        for p, v in zip(valeurs[:-1], valeurs[1:], strict=True)]
    fig = go.Figure(go.Funnel(
        y=etapes, x=valeurs, text=textes, textinfo="text", textposition="outside",
        marker=dict(color=couleurs[:len(valeurs)], line=dict(width=0)),
        connector=dict(fillcolor=t["bg-subtle"], line=dict(width=0)),
        textfont=dict(size=12, color=t["text-primary"]),
        hovertemplate="%{y} : %{x:,.0f}<extra></extra>"))
    return _base(fig, scheme, margin=dict(l=8, r=8, t=8, b=8),
                 xaxis=dict(type="log", showticklabels=False, showgrid=False, showline=False),
                 yaxis=dict(showgrid=False, tickfont=dict(size=13, color=t["text-primary"])))


def pyramide(classes: list[str], hommes: list, femmes: list, scheme: str, unite: str,
             alerte_hommes: bool = True) -> go.Figure:
    """Pyramide des âges : hommes à gauche, femmes à droite, même échelle ; valeurs masquées
    (sous le seuil) laissées vides."""
    t = tokens(scheme)
    h = [None if v is None or v != v else v for v in hommes]
    f = [None if v is None or v != v else v for v in femmes]
    borne = max([v for v in h + f if v is not None] or [1]) * 1.15
    fig = go.Figure()
    fig.add_trace(go.Bar(y=classes, x=[-v if v is not None else None for v in h], orientation="h",
                         name="Hommes", customdata=h,
                         marker=dict(color=t["grav-tue"] if alerte_hommes else t["data-neutre"],
                                     line=dict(width=0)),
                         hovertemplate="Hommes · %{y} ans : %{customdata:.1f} " + unite
                                       + "<extra></extra>"))
    fig.add_trace(go.Bar(y=classes, x=f, orientation="h", name="Femmes",
                         marker=dict(color=t["data-neutre-clair"] if alerte_hommes
                                     else t["data-neutre"], line=dict(width=0)),
                         hovertemplate="Femmes · %{y} ans : %{x:.1f} " + unite
                                       + "<extra></extra>"))
    graduations = [g for g in np.linspace(-borne, borne, 7)]
    fig.add_annotation(**_annot(t, -borne, 1.02, "← Hommes", t["text-secondary"],
                                xanchor="left", yref="paper", yanchor="bottom"))
    fig.add_annotation(**_annot(t, borne, 1.02, "Femmes →", t["text-secondary"],
                                xanchor="right", yref="paper", yanchor="bottom"))
    return _base(fig, scheme, barmode="overlay", bargap=0.12, showlegend=False,
                 margin=dict(l=8, r=8, t=28, b=8),
                 xaxis=dict(range=[-borne, borne], tickvals=graduations,
                            ticktext=[fmt_number(abs(g), 0) for g in graduations],
                            showgrid=True, gridcolor=t["border"]),
                 yaxis=dict(showgrid=False, tickfont=dict(size=11)))


def treemap(parents: list[str], enfants: list[str], tailles: list[float], couleurs: list,
            scheme: str, lib_taille: str, lib_couleur: str) -> go.Figure:
    """Treemap à deux niveaux : surface = `tailles`, couleur = `couleurs` (échelle séquentielle)."""
    t = tokens(scheme)
    seq = [t[f"seq-{i}"] for i in range(1, 6)]
    ids = [f"{p}/{e}" for p, e in zip(parents, enfants, strict=True)]
    tops = sorted(set(parents))
    tot_parent = {p: sum(s for pp, s in zip(parents, tailles, strict=True) if pp == p)
                  for p in tops}
    fig = go.Figure(go.Treemap(
        ids=tops + ids, labels=tops + list(enfants), parents=[""] * len(tops) + list(parents),
        values=[tot_parent[p] for p in tops] + list(tailles), branchvalues="total",
        marker=dict(colors=[None] * len(tops) + list(couleurs), colorscale=seq,
                    line=dict(color=t["bg-surface"], width=2), showscale=False,
                    pad=dict(t=22, l=3, r=3, b=3)),
        customdata=[[tot_parent[p], None] for p in tops]
        + [[s, c] for s, c in zip(tailles, couleurs, strict=True)],
        texttemplate="<b>%{label}</b><br>%{value:,.0f}", textfont=dict(size=12),
        hovertemplate=("<b>%{label}</b><br>" + lib_taille + " : %{customdata[0]:,.0f}"
                       "<br>" + lib_couleur + " : %{customdata[1]:.1f}<extra></extra>"),
        root=dict(color=t["bg-subtle"]), tiling=dict(pad=2)))
    return _base(fig, scheme, margin=dict(l=4, r=4, t=4, b=4))


FONDS_CARTE = {"light": "carto-positron", "dark": "carto-darkmatter"}


def choroplethe_tuiles(geojson, deps, noms, valeurs, scheme: str, unite: str,
                       selection=None) -> tuple[go.Figure, list[float]]:
    """Même carte que `choroplethe`, sur un fond de carte en ligne (tuiles Carto via MapLibre,
    sans clé d'API) ; demande une connexion, sinon seules les zones colorées s'affichent."""
    t = tokens(scheme)
    seq = [t[f"seq-{i}"] for i in range(1, 6)]
    vals = np.array(valeurs, dtype=float)
    bornes = classes_quantiles(vals)
    rang = (-vals).argsort().argsort() + 1
    ok = ~np.isnan(vals)
    n_valides = int(ok.sum())
    fig = go.Figure()
    if ok.any():
        cls = np.clip(np.searchsorted(bornes, vals[ok], side="right") - 1, 0, len(bornes) - 2)
        k = max(len(bornes) - 1, 1)
        echelle = []
        for i in range(k):
            echelle += [[i / k, seq[i]], [(i + 1) / k, seq[i]]]
        fig.add_trace(go.Choroplethmap(
            geojson=geojson, featureidkey="properties.code", locations=np.array(deps)[ok],
            z=cls, zmin=0, zmax=k - 1 if k > 1 else 1, colorscale=echelle, showscale=False,
            marker=dict(opacity=0.82, line=dict(color=t["bg-surface"], width=0.6)),
            customdata=np.column_stack([np.array(noms)[ok], vals[ok], rang[ok]]),
            hovertemplate=("<b>%{customdata[0]}</b><br>%{customdata[1]:.1f} " + unite
                           + f"<br>Rang %{{customdata[2]}} / {n_valides}<extra></extra>")))
    if (~ok).any():
        fig.add_trace(go.Choroplethmap(
            geojson=geojson, featureidkey="properties.code", locations=np.array(deps)[~ok],
            z=[0] * int((~ok).sum()), colorscale=[[0, t["seq-na"]], [1, t["seq-na"]]],
            showscale=False, marker=dict(opacity=0.8, line=dict(color=t["bg-surface"], width=0.6)),
            customdata=np.array(noms)[~ok],
            hovertemplate="<b>%{customdata}</b><br>Effectif trop faible<extra></extra>"))
    if selection:
        fig.add_trace(contour_selection_tuiles(geojson, selection, scheme))
    fig.update_layout(map=dict(style=FONDS_CARTE.get(scheme, "carto-positron"),
                               center=dict(lat=46.6, lon=2.4), zoom=4.35))
    _base(fig, scheme, margin=dict(l=0, r=0, t=0, b=0))
    return fig, list(bornes)


def contour_selection_tuiles(geojson, dep: str, scheme: str) -> go.Choroplethmap:
    t = tokens(scheme)
    entite = {"type": "FeatureCollection",
              "features": [f for f in geojson["features"] if f["properties"]["code"] == dep]}
    return go.Choroplethmap(
        geojson=entite, featureidkey="properties.code", locations=[dep], z=[0],
        colorscale=[[0, TRANSPARENT], [1, TRANSPARENT]], showscale=False,
        marker=dict(line=dict(color=t["accent"], width=3)), hoverinfo="skip")
