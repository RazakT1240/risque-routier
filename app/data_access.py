"""Lecture des Parquet pré-agrégés (G15) + filtres période / territoire.

Les callbacks ne font que filtrer, sommer et tracer : aucun calcul lourd ici.
Les formules d'indicateurs viennent de pipeline.indicators (définition unique).
"""

from __future__ import annotations

import json
from functools import cache

import pandas as pd
import yaml

from pipeline import config as C

PERIODE_CUMUL = "cumul"
TERRITOIRE_FRANCE = "FR"
DERNIERE_ANNEE = C.ANNEES[-1]
PREMIERE_ANNEE = C.ANNEES[0]
LIBELLE_PERIODE_CUMUL = f"{PREMIERE_ANNEE}–{DERNIERE_ANNEE}"
SOURCE_BAAC = "ONISR, fichiers BAAC 2019–2025"
SOURCE_INSEE = "INSEE, estimations de population au 1er janvier"


@cache
def table(nom: str) -> pd.DataFrame:
    return pd.read_parquet(C.PROCESSED / f"{nom}.parquet")


@cache
def modele(nom: str) -> dict:
    return json.loads((C.MODELS / f"{nom}.json").read_text(encoding="utf-8"))


@cache
def references() -> dict:
    return yaml.safe_load(C.REFERENCES.read_text(encoding="utf-8")) or {}


@cache
def geojson() -> dict:
    return json.loads(C.RAW_GEO.read_text(encoding="utf-8"))


@cache
def noms_departements() -> dict[str, str]:
    return {f["properties"]["code"]: f["properties"]["nom"] for f in geojson()["features"]}


def departements_metropole() -> list[dict]:
    noms = noms_departements()
    return [{"dep": d, "nom": noms[d]} for d in sorted(noms)]


def annees(periode: str | None) -> list[int]:
    if periode in (None, PERIODE_CUMUL):
        return list(C.ANNEES)
    return [int(periode)]


def annee_ref(periode: str | None) -> int:
    """Année des KPI : l'année choisie, ou la dernière année en cumul."""
    return DERNIERE_ANNEE if periode in (None, PERIODE_CUMUL) else int(periode)


def libelle_periode(periode: str | None) -> str:
    return LIBELLE_PERIODE_CUMUL if periode in (None, PERIODE_CUMUL) else str(periode)


def libelle_territoire(dep: str | None) -> str:
    if dep in (None, TERRITOIRE_FRANCE):
        return "France métropolitaine"
    return f"{noms_departements().get(dep, dep)} ({dep})"


def filtrer(df: pd.DataFrame, periode: str | None = None, dep: str | None = None,
            toutes_annees: bool = False) -> pd.DataFrame:
    masque = pd.Series(True, index=df.index)
    if not toutes_annees and "annee" in df.columns:
        masque &= df["annee"].isin(annees(periode))
    if dep not in (None, TERRITOIRE_FRANCE) and "dep" in df.columns:
        masque &= df["dep"] == dep
    if "metropole" in df.columns:
        masque &= df["metropole"]
    return df[masque]


def population(periode: str | None, dep: str | None) -> float:
    """Personnes-années sur la période (somme des populations annuelles)."""
    return float(filtrer(table("pop_dep"), periode, dep)["population"].sum())


def population_par_annee(dep: str | None) -> pd.Series:
    return filtrer(table("pop_dep"), dep=dep, toutes_annees=True).groupby("annee")[
        "population"].sum()


def puces_filtres(periode: str | None, dep: str | None, toutes_annees: bool = False) -> list[str]:
    puces = ["Toutes années" if toutes_annees else libelle_periode(periode)]
    if dep not in (None, TERRITOIRE_FRANCE):
        puces.append(libelle_territoire(dep))
    return puces
