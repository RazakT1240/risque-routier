"""Constructeurs de figures Plotly (DESIGN_SYSTEM.md §8) — une fonction par type de graphique.

Règles : tout en neutre, une seule couleur d'alerte (grav-tue) pour ce que le titre désigne (G10),
annotations directes plutôt que légende, aucun double axe Y (G11), formats français.
Chaque fonction reçoit `scheme` ('light' / 'dark') et lit les couleurs dans les tokens (G9).
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app.components.format import fmt_number, fmt_pct, fmt_ratio
from design.plotly_template import template_name
from design.tokens import FONT_SANS, FONT_SERIF, TRANSPARENT, tokens

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
                                    xanchor="left", xshift=10))
    fig.add_hline(y=100, line=dict(color=t["border"], width=1, dash="dot"))
    bande_2020(fig, t)
    return _base(fig, scheme, hovermode="x unified", showlegend=False,
                 margin=dict(l=8, r=150, t=28, b=8),
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
        derniere = max(i for i, v in enumerate(vals) if v is not None and not np.isnan(v))
        fig.add_annotation(**_annot(t, classes[derniere], vals[derniere], f"<b>{nom}</b>", c,
                                    xanchor="left", xshift=6))
    valides = [(i, v) for i, v in enumerate(hommes) if v is not None and not np.isnan(v)]
    if valides:
        i, v = max(valides, key=lambda iv: iv[1])
        fig.add_annotation(x=classes[i], y=v, text=f"Pic : {fmt_number(v, 0)} à {classes[i]} ans",
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
        # Contour ambre du département filtré (remplissage transparent)
        fig.add_trace(go.Choropleth(
            geojson=geojson, featureidkey="properties.code", locations=[selection], z=[0],
            colorscale=[[0, TRANSPARENT], [1, TRANSPARENT]], showscale=False,
            marker_line_color=t["accent"], marker_line_width=2.5, hoverinfo="skip"))
    fig.update_geos(fitbounds="locations", visible=False, projection_type="mercator",
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
    t = tokens(scheme)
    imax = int(np.nanargmax(valeurs)) if len(valeurs) else -1
    fig = go.Figure(go.Bar(
        x=heures, y=valeurs, marker_line_width=0, marker_cornerradius=2,
        marker_color=[t["grav-tue"] if i == imax else t["data-neutre"]
                      for i in range(len(valeurs))],
        customdata=[fmt(v) for v in valeurs],
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

def petits_multiples(annees, series: dict[str, list], alerte: str, scheme: str,
                     cols: int = 3) -> go.Figure:
    t = tokens(scheme)
    noms = list(series)
    rows = int(np.ceil(len(noms) / cols))
    fig = make_subplots(rows=rows, cols=cols, shared_yaxes=True, shared_xaxes=True,
                        subplot_titles=noms, vertical_spacing=0.12, horizontal_spacing=0.05)
    vmax = max(max(v for v in s if v is not None) for s in series.values())
    for k, nom in enumerate(noms):
        r, c = k // cols + 1, k % cols + 1
        vals = series[nom]
        coul = t["grav-tue"] if nom == alerte else t["data-neutre"]
        fig.add_trace(go.Scatter(x=annees, y=vals, mode="lines", line=dict(color=coul, width=2),
                                 hovertemplate=f"{nom} · %{{x}} : %{{y:.0f}}<extra></extra>"),
                      row=r, col=c)
        fig.add_trace(go.Scatter(x=[annees[-1]], y=[vals[-1]], mode="markers+text",
                                 marker=dict(color=coul, size=6), text=[fmt_number(vals[-1])],
                                 textposition="top left", textfont=dict(size=11, color=coul),
                                 hoverinfo="skip"), row=r, col=c)
        fig.add_hline(y=100, line=dict(color=t["border"], width=1, dash="dot"), row=r, col=c)
        fig.add_vrect(x0=2019.5, x1=2020.5, fillcolor=t["data-neutre-clair"], opacity=0.35,
                      line_width=0, layer="below", row=r, col=c)
    fig.update_annotations(font=dict(family=FONT_SERIF, size=14, color=t["text-primary"]))
    fig.update_xaxes(dtick=3, tickfont=dict(size=10))
    fig.update_yaxes(range=[0, vmax * 1.22], tickfont=dict(size=10), nticks=4)
    return _base(fig, scheme, showlegend=False, margin=dict(l=8, r=8, t=28, b=8))


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
    fig.add_hline(y=seuil, line=dict(color=t["grav-tue"], width=1.5, dash="dash"))
    fig.add_annotation(**_annot(t, n80, seuil,
                                f"<b>{n80 + 1} segments = {fmt_pct(cumul[n80], 0)}</b>",
                                t["grav-tue"], xanchor="left", yanchor="top", xshift=10,
                                yshift=-6))
    return _base(fig, scheme, showlegend=False, margin=dict(l=8, r=8, t=16, b=8),
                 xaxis=dict(tickangle=-35, tickfont=dict(size=11)),
                 yaxis=dict(range=[0, 105], ticksuffix=" %"))
