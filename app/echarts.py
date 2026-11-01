"""Graphiques ECharts (jauges, rose des mois, radar) : options construites ici depuis les tokens,
rendues côté client par app/assets/echarts_route.js (bibliothèque dans assets/vendor/).

Chaque fonction renvoie une « charge » {"option", "tableau", "fmt"} :
- `option` : option ECharts sérialisable (aucune fonction JS) ;
- `tableau` : lignes (série, catégorie, valeur) pour « Voir les données » ;
- `fmt` : format français des valeurs appliqué côté client (décimales, suffixe).
"""

from __future__ import annotations

import math

from app.components.format import fmt_number
from design.tokens import FONT_SANS, tokens

MOIS_COURTS = ["Janv.", "Févr.", "Mars", "Avr.", "Mai", "Juin", "Juil.", "Août", "Sept.", "Oct.",
               "Nov.", "Déc."]


def _charge(option: dict, tableau=None, decimales: int = 0, suffixe: str = "") -> dict:
    option.setdefault("textStyle", {"fontFamily": FONT_SANS})
    return {"option": option, "tableau": tableau or [],
            "fmt": {"decimales": decimales, "suffixe": suffixe}}


def _infobulle(t: dict, **kw) -> dict:
    return {"backgroundColor": t["bg-surface"], "borderColor": t["border"], "borderWidth": 1,
            "textStyle": {"color": t["text-primary"], "fontSize": 13, "fontFamily": FONT_SANS},
            "extraCssText": "border-radius:8px;box-shadow:none", **kw}


def message(texte: str, scheme: str) -> dict:
    """Charge vide portant un message (effectif trop faible, donnée indisponible)."""
    t = tokens(scheme)
    return _charge({"graphic": [{"type": "text", "left": "center", "top": "middle", "style": {
        "text": texte, "fill": t["text-muted"], "fontSize": 14, "fontFamily": FONT_SANS}}]})


def jauge(valeur: float, reference: float | None, vmin: float, vmax: float, scheme: str,
          suffixe: str = "", lib_ref: str = "", decimals: int = 1,
          plus_est_mauvais: bool = True) -> dict:
    """Jauge en arc : progression rouge jusqu'à la valeur, trait de repère à la référence,
    variation ▲▼ sous le chiffre (l'information ne passe pas par la seule couleur)."""
    t = tokens(scheme)
    arc = {"type": "gauge", "startAngle": 210, "endAngle": -30, "min": vmin, "max": vmax,
           "radius": "88%", "center": ["50%", "58%"], "splitNumber": 5}
    variation = ""
    couleur_var = t["text-secondary"]
    if reference is not None:
        d = valeur - reference
        fleche = "▲" if d > 0 else "▼" if d < 0 else "="
        # Écart en points (taux pour 100) ; la référence est nommée sous la jauge
        variation = f"{fleche} {fmt_number(d, decimals, signe=True)} pt"
        variation += "s" if abs(round(d, decimals)) >= 2 else ""
        hausse_mauvaise = (d > 0) == plus_est_mauvais
        couleur_var = t["delta-hausse"] if hausse_mauvaise and d else (
            t["delta-baisse"] if d else t["text-secondary"])
    series = [{
        **arc,
        "progress": {"show": True, "width": 16, "roundCap": True,
                     "itemStyle": {"color": t["grav-tue"]}},
        "axisLine": {"roundCap": True, "lineStyle": {"width": 16, "color": [[1, t["seq-na"]]]}},
        "pointer": {"show": False}, "anchor": {"show": False},
        "axisTick": {"show": False},
        "splitLine": {"distance": -16, "length": 16,
                      "lineStyle": {"color": t["bg-surface"], "width": 2}},
        "axisLabel": {"distance": 24, "color": t["text-muted"], "fontSize": 11},
        "detail": {"valueAnimation": True, "offsetCenter": [0, "-4%"], "fontSize": 38,
                   "fontWeight": 600, "fontFamily": FONT_SANS, "color": t["text-primary"]},
        "title": {"offsetCenter": [0, "30%"], "fontSize": 13, "fontWeight": 600,
                  "color": couleur_var},
        "data": [{"value": valeur, "name": variation}],
    }]
    if reference is not None:
        series.append({
            **arc, "z": 5,
            "pointer": {"show": True, "icon": "rect", "width": 4, "length": "22%",
                        "offsetCenter": [0, "-71%"], "itemStyle": {"color": t["text-primary"]}},
            "axisLine": {"show": False}, "axisTick": {"show": False},
            "splitLine": {"show": False}, "axisLabel": {"show": False},
            "anchor": {"show": False}, "detail": {"show": False}, "title": {"show": False},
            "data": [{"value": reference}]})
    option = {"series": series}
    if reference is not None and lib_ref:
        option["graphic"] = [{"type": "text", "left": "center", "bottom": 6, "style": {
            "text": f"Trait : {lib_ref} ({fmt_number(reference, decimals)}{suffixe})",
            "fill": t["text-muted"], "fontSize": 12, "fontFamily": FONT_SANS}}]
    tableau = [["", "Valeur", valeur]]
    if reference is not None:
        tableau.append(["", f"Repère ({lib_ref})", reference])
    return _charge(option, tableau, decimals, suffixe)


def rose_mois(valeurs: list, scheme: str, unite: str = "tués") -> dict:
    """Barres radiales : un secteur par mois ; le mois le plus lourd en rouge."""
    t = tokens(scheme)
    imax = max(range(12), key=lambda i: valeurs[i])
    data = [{"value": v, "itemStyle": {"color": t["grav-tue"] if i == imax else t["data-neutre"]}}
            for i, v in enumerate(valeurs)]
    option = {
        "polar": {"radius": ["16%", "80%"], "center": ["50%", "52%"]},
        "angleAxis": {"type": "category", "data": MOIS_COURTS, "startAngle": 90,
                      "clockwise": True, "axisLine": {"lineStyle": {"color": t["border"]}},
                      "axisTick": {"show": False},
                      "axisLabel": {"color": t["text-secondary"], "fontSize": 12}},
        "radiusAxis": {"show": True, "axisLabel": {"show": False}, "axisLine": {"show": False},
                       "axisTick": {"show": False},
                       "splitLine": {"lineStyle": {"color": t["border"], "type": "dashed"}}},
        "tooltip": _infobulle(t, trigger="item"),
        "series": [{"type": "bar", "coordinateSystem": "polar", "name": unite.capitalize(),
                    "data": data, "roundCap": True, "barCategoryGap": "18%",
                    "emphasis": {"focus": "self"}}],
    }
    return _charge(option, [["", m, v] for m, v in zip(MOIS_COURTS, valeurs, strict=True)],
                   0, f" {unite}")


def radar(axes: list[str], series: dict[str, list], couleurs: dict[str, str],
          scheme: str) -> dict:
    """Radar de profils (même unité, %) ; contextes sous le seuil laissés vides ('-')."""
    t = tokens(scheme)
    vals = [v for s in series.values() for v in s if v is not None]
    vmax = max(10, math.ceil(max(vals, default=10) / 10) * 10)
    option = {
        "legend": {"bottom": 0, "icon": "roundRect", "itemWidth": 14, "itemHeight": 8,
                   "textStyle": {"color": t["text-secondary"], "fontSize": 12}},
        "tooltip": _infobulle(t, trigger="item"),
        "radar": {"indicator": [{"name": a, "max": vmax} for a in axes], "radius": "66%",
                  "center": ["50%", "48%"], "splitNumber": 4, "shape": "polygon",
                  "axisName": {"color": t["text-secondary"], "fontSize": 12},
                  "splitLine": {"lineStyle": {"color": t["border"]}},
                  "splitArea": {"show": False},
                  "axisLine": {"lineStyle": {"color": t["border"]}}},
        "series": [{"type": "radar", "symbolSize": 6, "data": [
            {"name": nom, "value": [v if v is not None else "-" for v in s],
             "itemStyle": {"color": couleurs[nom]},
             "lineStyle": {"color": couleurs[nom], "width": 2.5},
             "areaStyle": {"color": couleurs[nom], "opacity": 0.14}}
            for nom, s in series.items()]}],
    }
    tableau = [[nom, a, v] for nom, s in series.items() for a, v in zip(axes, s, strict=True)]
    return _charge(option, tableau, 1, " %")
