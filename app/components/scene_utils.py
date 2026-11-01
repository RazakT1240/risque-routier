"""Outils communs aux pages de scène : entrées des callbacks, séries, KPI standard."""

from __future__ import annotations

import pandas as pd
from dash import Input

from app import data_access as da
from app.components.format import NA, delta, fmt_number, fmt_pct
from pipeline import config as C
from pipeline.indicators import masque_seuil

ENTREES = [Input("filtres", "data"), Input("theme-toggle", "computedColorScheme")]
SEUIL = C.SEUIL_EFFECTIF


def lire(filtres: dict | None, scheme: str | None):
    f = filtres or {}
    return (f.get("periode") or str(da.DERNIERE_ANNEE), f.get("dep") or da.TERRITOIRE_FRANCE,
            scheme or "light")


def par_annee(nom: str, dep: str, cols: list[str], **filtres_col) -> pd.DataFrame:
    """Somme par année (toutes années) pour un territoire, colonnes `cols`."""
    df = da.filtrer(da.table(nom), dep=dep, toutes_annees=True)
    for col, val in filtres_col.items():
        df = df[df[col] == val]
    out = df.groupby("annee")[cols].sum().reindex(C.ANNEES, fill_value=0)
    return out


def valeur(serie: pd.Series, annees: list[int]):
    return float(serie.loc[annees].sum())


def taux_masque(num: float, den: float, eff: float, facteur: float = 1.0):
    """Taux = num / den × facteur, masqué si l'effectif est sous le seuil (G6)."""
    if not den or eff < SEUIL:
        return None
    return float(masque_seuil(pd.Series([num / den * facteur]), pd.Series([eff])).iloc[0])


def deltas_annuels(serie: pd.Series, periode: str, plus_est_mauvais=True,
                   decimals: int = 1) -> list[dict]:
    """▲▼ vs N−1 et vs 2019 pour l'année choisie ; rien en cumul."""
    if periode == da.PERIODE_CUMUL:
        return [{"texte": f"Cumul {da.LIBELLE_PERIODE_CUMUL}", "sens": "neutre"}]
    a = int(periode)
    out = []
    if a - 1 in serie.index:
        out.append(delta(serie[a], serie[a - 1], str(a - 1), plus_est_mauvais, decimals))
    if a != da.PREMIERE_ANNEE:
        out.append(delta(serie[a], serie[da.PREMIERE_ANNEE], str(da.PREMIERE_ANNEE),
                         plus_est_mauvais, decimals))
    return out


def fmt_ou_na(v, decimals=0, pct=False):
    if v is None:
        return NA
    return fmt_pct(v, decimals) if pct else fmt_number(v, decimals)


def libelle_kpi(base: str, periode: str) -> str:
    return f"{base} · {da.libelle_periode(periode)}"
