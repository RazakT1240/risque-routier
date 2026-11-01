"""Tables préparées (BRIEF §2.3–2.4) : usagers enrichis, accidents, expositions, météo."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from pipeline import config as C

log = logging.getLogger(__name__)


# --- Météo ---------------------------------------------------------------

def meteo_categorie(df: pd.DataFrame) -> pd.Series:
    """gel prioritaire, puis pluie forte, pluie faible, sec."""
    rr = df["rr_moy_mm"]
    cat = np.select(
        [df["part_stations_gel"] >= C.METEO_GEL_PART, rr >= C.METEO_PLUIE_FORTE_MM,
         rr >= C.METEO_SEC_MAX_MM],
        ["gel", "pluie forte", "pluie faible"], default="sec")
    return pd.Series(cat, index=df.index)


def premiere_pluie(df: pd.DataFrame) -> pd.Series:
    """1er jour >= 1 mm après au moins 7 jours secs (< 0,2 mm) consécutifs, par département.

    Suppose df trié par (dep, date) sans trou de dates.
    """
    sec = df["rr_moy_mm"] < C.METEO_SEC_MAX_MM
    # Longueur de la série de jours secs se terminant la veille
    bloc = (~sec).groupby(df["dep"]).cumsum()
    serie_secs = sec.groupby([df["dep"], bloc]).cumsum()
    veille = serie_secs.groupby(df["dep"]).shift(1).fillna(0)
    return ((df["rr_moy_mm"] >= C.PLUIE_JOUR_MM)
            & (veille >= C.PREMIERE_PLUIE_JOURS_SECS)).astype("int8")


def prepare_meteo(meteo: pd.DataFrame) -> pd.DataFrame:
    # Calendrier complet : un jour manquant casse la série de jours secs (ni sec ni pluvieux)
    dates = pd.date_range(meteo["date"].min(), meteo["date"].max(), freq="D")
    grille = pd.MultiIndex.from_product([sorted(meteo["dep"].unique()), dates],
                                        names=["dep", "date"]).to_frame(index=False)
    df = grille.merge(meteo, on=["dep", "date"], how="left")
    manquants = df["rr_moy_mm"].isna()
    if manquants.any():
        log.info("météo : %d département-jours absents, exclus après calcul", manquants.sum())
    df["premiere_pluie"] = premiere_pluie(df)
    df = df[~manquants].reset_index(drop=True)
    df["meteo_cat"] = meteo_categorie(df)
    return df


# --- Usagers -------------------------------------------------------------

def type_usager(catu: pd.Series, catv: pd.Series) -> pd.Series:
    out = pd.Series("Autre", index=catu.index, dtype="object")
    for libelle, codes in C.TYPE_USAGER_CATV.items():
        out[catv.isin(codes).fillna(False).to_numpy()] = libelle
    out[(catu == 3).fillna(False).to_numpy()] = "Piéton"
    return pd.Categorical(out, categories=C.TYPE_USAGER_ORDRE)


def classe_age(age: pd.Series) -> pd.Series:
    idx = (age // 5).clip(upper=19)
    out = pd.Series(pd.NA, index=age.index, dtype="object")
    ok = idx.notna()
    out[ok] = [C.CLASSES_AGE[int(i)] for i in idx[ok]]
    return pd.Categorical(out, categories=C.CLASSES_AGE)


def _map_cat(s: pd.Series, mapping: dict, ordre: list, defaut=None) -> pd.Categorical:
    out = s.map(mapping)
    if defaut is not None:
        out = out.where(s.isna() | out.notna(), defaut)
    return pd.Categorical(out, categories=ordre)


def equipement_casque(secu: pd.DataFrame) -> pd.Categorical:
    """Casque si un des 3 équipements vaut 2 ; « Aucun équipement » si secu1 = 0 sans casque ;
    sinon « Indéterminé » (8 = non déterminable, manquant, autre équipement seul)."""
    casque = (secu == C.SECU_CASQUE).any(axis=1).to_numpy()
    aucun = (secu["secu1"] == 0).fillna(False).to_numpy() & ~casque
    out = np.select([casque, aucun], ["Casque", "Aucun équipement"], default="Indéterminé")
    return pd.Categorical(out, categories=C.CASQUE_ORDRE)


def enrich_caract(caract: pd.DataFrame, lieux: pd.DataFrame, meteo: pd.DataFrame) -> pd.DataFrame:
    df = caract.merge(lieux.drop(columns="annee"), on="Num_Acc", how="left", validate="1:1")
    df["metropole"] = ~df["dep"].isin(C.DEP_OUTRE_MER)
    df["date"] = pd.to_datetime(dict(year=df["an"], month=df["mois"], day=df["jour"]))
    df["jour_semaine"] = df["date"].dt.dayofweek.astype("int8")      # 0 = lundi
    df["heure"] = pd.to_numeric(df["hrmn"].str.split(":").str[0], errors="coerce").astype("Int8")
    df["weekend"] = df["jour_semaine"] >= 5
    df["nuit"] = df["lum"].isin(C.NUIT_LUM).astype("boolean").mask(df["lum"].isna())
    df["catr_groupe"] = _map_cat(df["catr"], C.CATR_GROUPE, C.CATR_GROUPE_ORDRE)
    df["lum_groupe"] = _map_cat(df["lum"], C.LUM_GROUPE, C.LUM_GROUPE_ORDRE)
    df["agg_lib"] = df["agg"].map(C.AGG)
    met = meteo[["dep", "date", "meteo_cat", "premiere_pluie"]]
    df = df.merge(met, on=["dep", "date"], how="left", validate="m:1")
    df["premiere_pluie"] = df["premiere_pluie"].astype("Int8")
    return df


def build_usagers_enrichis(caract_e: pd.DataFrame, vehicules: pd.DataFrame,
                           usagers: pd.DataFrame) -> pd.DataFrame:
    veh = vehicules[["Num_Acc", "id_vehicule", "catv", "obs", "obsm", "motor"]]
    df = usagers.merge(veh, on=["Num_Acc", "id_vehicule"], how="left", validate="m:1")
    cols_acc = ["Num_Acc", "dep", "metropole", "date", "mois", "jour_semaine", "heure",
                "weekend", "lum", "lum_groupe", "nuit", "agg", "agg_lib", "atm", "col", "catr",
                "catr_groupe", "vma", "surf", "meteo_cat", "premiere_pluie"]
    df = df.merge(caract_e[cols_acc], on="Num_Acc", how="left", validate="m:1")

    age = df["annee"] - df["an_nais"]
    df["age"] = age.where(age.between(C.AGE_MIN, C.AGE_MAX))
    df["classe_age"] = classe_age(df["age"])
    df["sexe_lib"] = df["sexe"].map(C.SEXE)
    df["type_usager"] = type_usager(df["catu"], df["catv"])
    df["obs_groupe"] = _map_cat(df["obs"], C.OBS_GROUPE, C.OBS_GROUPE_ORDRE, defaut=C.OBS_AUTRE)
    df["casque"] = equipement_casque(df[["secu1", "secu2", "secu3"]])

    grav = df["grav"]
    df["victime"] = grav.isin([2, 3, 4]).astype("boolean").mask(grav.isna())
    df["grave"] = grav.isin([2, 3]).astype("boolean").mask(grav.isna())
    df["tue"] = (grav == 2).astype("boolean")
    df["hospitalise"] = (grav == 3).astype("boolean")
    df["leger"] = (grav == 4).astype("boolean")
    # Usagers en fuite (depuis 2021) : sexe et année de naissance absents
    df["en_fuite"] = (df["annee"] >= 2021) & df["sexe"].isna() & df["an_nais"].isna()
    return df


def build_accidents(caract_e: pd.DataFrame, usagers_e: pd.DataFrame) -> pd.DataFrame:
    g = usagers_e.groupby("Num_Acc").agg(
        nb_usagers=("id_usager", "size"), nb_victimes=("victime", "sum"),
        nb_graves=("grave", "sum"), nb_tues=("tue", "sum"))
    df = caract_e.merge(g, on="Num_Acc", how="left", validate="1:1")
    for col in g.columns:
        df[col] = df[col].fillna(0).astype("int32")
    return df


# --- Expositions ---------------------------------------------------------

def build_expo_population(insee: pd.DataFrame) -> pd.DataFrame:
    df = insee.copy()
    df["metropole"] = ~df["dep"].isin(C.DEP_OUTRE_MER)
    df["classe_age"] = pd.Categorical(df["classe_age"], categories=C.CLASSES_AGE)
    return df


def build_expo_parc(sdes: pd.DataFrame) -> pd.DataFrame:
    df = sdes[sdes["annee"].isin(C.ANNEES)].copy()
    df["metropole"] = ~df["dep"].isin(C.DEP_OUTRE_MER)
    return df.reset_index(drop=True)
