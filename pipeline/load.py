"""Lecture des données brutes et corrections des pièges connus (BRIEF §2.1).

Rien n'est écrit dans data/ brut (G7). Chaque fonction renvoie un DataFrame propre.
"""

from __future__ import annotations

import json
import logging

import numpy as np
import pandas as pd

from pipeline import config as C

log = logging.getLogger(__name__)

TEXTE_MANQUANT = {"", "N/A", "."}


def _read_raw(path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";", dtype=str, keep_default_na=False, encoding="utf-8")
    # 2025 : "id_vehicule\n" ; on nettoie tous les noms par sécurité
    df.columns = df.columns.str.strip()
    # Espaces en tête (" -1") dans toutes les tables, "N/A" littéral dans lieux et caract
    df = df.apply(lambda s: s.str.strip())
    return df.replace(dict.fromkeys(TEXTE_MANQUANT, pd.NA))


def _to_codes(df: pd.DataFrame, cols: list[str], table: str, annee: int) -> pd.DataFrame:
    for col in cols:
        raw = df[col]
        num = pd.to_numeric(raw, errors="coerce")
        bad = int((num.isna() & raw.notna()).sum())
        if bad:
            log.warning("%s-%s : %d valeurs non numériques dans %s -> manquant",
                        table, annee, bad, col)
        df[col] = num.astype("Int64").mask(num == -1)
    for col in C.COLS_ZERO_MANQUANT.get(table, []):
        df[col] = df[col].mask(df[col] == 0)
    return df


def normalize_dep(dep: pd.Series) -> pd.Series:
    """'1' -> '01' ; 2A, 2B et codes à 3 caractères inchangés."""
    dep = dep.astype("string").str.strip().str.upper()
    return dep.where(dep.str.len() != 1, dep.str.zfill(2))


def load_baac(table: str, annee: int) -> pd.DataFrame:
    path = C.RAW_BAAC / str(annee) / f"{table}-{annee}.csv"
    df = _read_raw(path)

    if table == "caract" and "Accident_Id" in df.columns:          # 2022
        df = df.rename(columns={"Accident_Id": "Num_Acc"})
    if table == "vehicules":
        if list(df.columns) != C.COLS_VEHICULES_2025:
            raise ValueError(f"{path.name} : colonnes inattendues {list(df.columns)}")
    if table == "usagers" and "id_usager" not in df.columns:       # 2019-2020
        rang = df.groupby("Num_Acc").cumcount() + 1
        df.insert(1, "id_usager", df["Num_Acc"] + "_" + rang.astype(str))

    df = _to_codes(df, C.COLS_CODES[table], table, annee)
    if table == "usagers":
        df["actp"] = df["actp"].mask(df["actp"].isin(C.ACTP_MANQUANT))

    if table == "caract":
        df["dep"] = normalize_dep(df["dep"])
        for col in ("lat", "long"):
            df[col] = pd.to_numeric(df[col].str.replace(",", ".", regex=False),
                                    errors="coerce")
    if table == "lieux":
        df["vma"] = df["vma"].where(df["vma"].isin(C.VMA_VALIDES))
        n_avant = len(df)
        df = df.drop_duplicates("Num_Acc", keep="first").reset_index(drop=True)
        if n_avant != len(df):
            log.info("lieux-%s : %d doublons de Num_Acc retirés (1re ligne gardée)",
                     annee, n_avant - len(df))
    df.insert(0, "annee", annee)
    return df


def load_baac_all(table: str) -> pd.DataFrame:
    frames = [load_baac(table, a) for a in C.ANNEES]
    df = pd.concat(frames, ignore_index=True)
    log.info("%s : %d lignes sur %d années", table, len(df), len(frames))
    return df


def load_meteo() -> pd.DataFrame:
    df = pd.read_csv(C.RAW_METEO, sep=";", dtype={"dep": str})
    df["date"] = pd.to_datetime(df["date"])
    df["dep"] = normalize_dep(df["dep"])
    # Corse codée "20" dans la météo, 2A / 2B dans les BAAC : on duplique
    corse = df[df["dep"] == "20"]
    df = pd.concat([df[df["dep"] != "20"], corse.assign(dep="2A"), corse.assign(dep="2B")],
                   ignore_index=True)
    return df.sort_values(["dep", "date"]).reset_index(drop=True)


def _classe_insee(label: str) -> str:
    """'0 à 4 ans' -> '0-4' ; '95 ans et plus' -> '95+'."""
    label = str(label).strip()
    if "et plus" in label:
        return label.split()[0] + "+"
    debut, fin = label.replace(" ans", "").split(" à ")
    return f"{debut}-{fin}"


def load_insee() -> pd.DataFrame:
    """Population au 1er janvier : dép. × année × sexe × classe d'âge (format long)."""
    frames = []
    for annee in C.ANNEES:
        raw = pd.read_excel(C.RAW_INSEE, sheet_name=str(annee), header=None)
        blocs, classes = raw.iloc[3], raw.iloc[4]
        data = raw.iloc[5:].copy()
        data[0] = data[0].map(lambda v: str(int(v)) if isinstance(v, (int, float, np.integer))
                              and not pd.isna(v) else v)
        code = data[0].astype("string").str.strip()
        est_dep = code.str.fullmatch(r"\d{2}|2[AB]|97\d").fillna(False)
        data = data[est_dep.to_numpy()]
        bloc_courant = None
        for j in range(2, raw.shape[1]):
            if pd.notna(blocs[j]):
                bloc_courant = str(blocs[j]).strip()
            classe = str(classes[j]).strip()
            if bloc_courant not in ("Hommes", "Femmes") or classe == "Total":
                continue
            frames.append(pd.DataFrame({
                "annee": annee, "dep": data[0].astype(str).str.strip(),
                "nom_dep": data[1].astype(str).str.strip(),
                "sexe": "Homme" if bloc_courant == "Hommes" else "Femme",
                "classe_age": _classe_insee(classe),
                "population": pd.to_numeric(data[j]).astype("int64"),
            }))
        _check_insee_totaux(raw, data, annee)
    return pd.concat(frames, ignore_index=True)


def _check_insee_totaux(raw: pd.DataFrame, data: pd.DataFrame, annee: int) -> None:
    """Contrôle BRIEF §1 : somme des classes = Total, pour chaque bloc et chaque ligne."""
    classes = raw.iloc[4]
    cols_total = [j for j in range(2, raw.shape[1]) if str(classes[j]).strip() == "Total"]
    debut = 2
    for jt in cols_total:
        somme = data.iloc[:, debut:jt].apply(pd.to_numeric).sum(axis=1)
        total = pd.to_numeric(data.iloc[:, jt])
        if not (somme == total).all():
            raise ValueError(f"INSEE {annee} : somme des classes != Total (colonne {jt})")
        debut = jt + 1


def load_sdes() -> pd.DataFrame:
    """Parc au 1er janvier : dép. × année × groupe (VP, VUL, PL, TCP), dep 00 exclu."""
    df = pd.read_csv(C.RAW_SDES, sep=";", dtype={"dep": str})
    df["dep"] = normalize_dep(df["dep"])
    df = df[df["dep"] != "00"]
    cols = [f"parc_{a}" for a in C.ANNEES]
    long = df.melt(id_vars=["dep", "groupe"], value_vars=cols, var_name="annee",
                   value_name="parc")
    long["annee"] = long["annee"].str[-4:].astype(int)
    return long.groupby(["dep", "annee", "groupe"], as_index=False)["parc"].sum()


def load_noms_dep() -> dict[str, str]:
    gj = json.loads(C.RAW_GEO_OM.read_text(encoding="utf-8"))
    return {f["properties"]["code"]: f["properties"]["nom"] for f in gj["features"]}
