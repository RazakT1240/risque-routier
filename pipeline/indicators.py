"""Définitions uniques des indicateurs (BRIEF §3) et agrégats par scène.

Convention : toute colonne `taux_<x>` est accompagnée de `eff_<x>`, l'effectif de victimes
(ou d'accidents) sur lequel le taux repose ; `masque_seuil` met le taux à NaN sous le seuil (G6).
Les agrégats ne contiennent que des comptages additifs, sauf s08 (table de la page Données).
"""

from __future__ import annotations

import pandas as pd

from pipeline import config as C

FLAGS = ["victime", "tue", "hospitalise", "leger", "grave"]
COMPTES = {"victime": "victimes", "tue": "tues", "hospitalise": "hospitalises",
           "leger": "legers", "grave": "graves"}


# --- Formules (une seule définition par indicateur) ------------------------

def masque_seuil(taux: pd.Series, effectif: pd.Series, seuil: int = C.SEUIL_EFFECTIF) -> pd.Series:
    return taux.where(effectif >= seuil)


def letalite(tues, victimes):
    """Tués pour 100 victimes."""
    return tues / victimes * 100


def taux_gravite(tues, hospitalises, victimes):
    """(Tués + hospitalisés) / victimes, en %."""
    return (tues + hospitalises) / victimes * 100


def pour_100k(n, population):
    return n / population * 100_000


def par_million(n, population):
    return n / population * 1_000_000


def pour_10k_vehicules(accidents, parc):
    return accidents / parc * 10_000


def base_100(valeur, valeur_ref):
    return valeur / valeur_ref * 100


# --- Agrégation ----------------------------------------------------------

def agg_usagers(u: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    g = (u.groupby(keys, observed=True, dropna=False)[FLAGS].sum()
         .rename(columns=COMPTES))
    g["impliques"] = u.groupby(keys, observed=True, dropna=False).size()
    return g.reset_index().astype({c: "int32" for c in [*COMPTES.values(), "impliques"]})


def agg_accidents(a: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    a = a.assign(mortel=(a["nb_tues"] > 0).astype("int32"))
    g = a.groupby(keys, observed=True, dropna=False).agg(
        accidents=("Num_Acc", "size"), accidents_mortels=("mortel", "sum"))
    return g.reset_index()


def build_scenes(u: pd.DataFrame, acc: pd.DataFrame, pop: pd.DataFrame,
                 parc: pd.DataFrame, vehicules: pd.DataFrame,
                 noms: dict[str, str]) -> dict[str, pd.DataFrame]:
    um = u[u["metropole"]]
    am = acc[acc["metropole"]]
    out: dict[str, pd.DataFrame] = {}

    out["pop_dep"] = (pop.groupby(["annee", "dep", "metropole"], as_index=False)["population"]
                      .sum())

    # Scène 02 (et 04 matrice, 06) : gravité par type d'usager, route, agglomération
    out["s02_gravite"] = agg_usagers(um, ["annee", "dep", "type_usager", "catr_groupe",
                                          "agg_lib"])
    out["s02_accidents"] = agg_accidents(am, ["annee", "dep", "agg_lib", "catr_groupe"])

    # Scène 03 : bascules vitesse / lumière / obstacle
    out["s03_vma"] = agg_usagers(um, ["annee", "dep", "agg_lib", "vma"])
    out["s03_lum"] = agg_usagers(um, ["annee", "dep", "agg_lib", "lum_groupe"])
    out["s03_obs"] = agg_usagers(um, ["annee", "dep", "agg_lib", "obs_groupe"])

    # Scène 04 : âge × sexe (avec population), casque des 2RM
    out["s04_age"] = agg_usagers(um, ["annee", "dep", "sexe_lib", "classe_age", "type_usager"])
    out["s04_casque"] = agg_usagers(um[um["type_usager"] == "2RM"],
                                    ["annee", "dep", "casque"])

    # Scène 05 : heatmap jour × heure
    hm_acc = agg_accidents(am, ["annee", "dep", "jour_semaine", "heure"])
    hm_usa = agg_usagers(um, ["annee", "dep", "jour_semaine", "heure"])
    out["s05_heatmap"] = hm_acc.merge(hm_usa, on=["annee", "dep", "jour_semaine", "heure"],
                                      how="outer").fillna(0)

    # Exposition parc : accidents impliquant au moins un véhicule du groupe
    out["ind_parc"] = build_ind_parc(acc, vehicules, parc)

    # Scène 05 : taux départementaux, par année et cumulés (métropole)
    out["ind_territoires"] = build_territoires(um, out["pop_dep"], noms)

    # Scène 08 : table Données (département × année, DOM compris)
    out["s08_donnees"] = build_s08(u, acc, out["pop_dep"], noms)
    return out


PERIODE_CUMUL = f"{C.ANNEES[0]}–{C.ANNEES[-1]}"


def build_territoires(um: pd.DataFrame, pop_dep: pd.DataFrame,
                      noms: dict[str, str]) -> pd.DataFrame:
    """Taux par département, pour chaque année et pour le cumul de la période.

    Cumul : victimes cumulées / somme des populations annuelles (personnes-années).
    Le cumul évite que le seuil G6 masque les départements peu peuplés.
    """
    g = agg_usagers(um, ["annee", "dep"])
    pop = pop_dep[pop_dep["metropole"]].drop(columns="metropole")
    an = g.merge(pop, on=["annee", "dep"], how="right").fillna(0)
    an["periode"] = an["annee"].astype(str)
    cols = ["victimes", "tues", "hospitalises", "graves", "population"]
    cum = an.groupby("dep", as_index=False)[cols].sum().assign(periode=PERIODE_CUMUL)
    df = pd.concat([an[["periode", "dep", *cols]], cum], ignore_index=True)
    df["nom_dep"] = df["dep"].map(noms)
    df["eff_victimes_100k"] = df["victimes"]
    df["taux_victimes_100k"] = masque_seuil(pour_100k(df["victimes"], df["population"]),
                                            df["victimes"])
    df["eff_tues_million"] = df["tues"]
    df["taux_tues_million"] = masque_seuil(par_million(df["tues"], df["population"]),
                                           df["tues"])
    df["eff_letalite"] = df["victimes"]
    df["taux_letalite"] = masque_seuil(letalite(df["tues"], df["victimes"]), df["victimes"])
    for col in ["victimes", "tues", "hospitalises", "graves", "population"]:
        df[col] = df[col].astype("int64")
    return df


def build_ind_parc(acc: pd.DataFrame, vehicules: pd.DataFrame, parc: pd.DataFrame) -> pd.DataFrame:
    frames = []
    v = vehicules.merge(acc[["Num_Acc", "dep"]], on="Num_Acc", how="inner")
    for groupe, codes in C.GROUPE_PARC_CATV.items():
        n = (v[v["catv"].isin(codes).fillna(False)]
             .drop_duplicates(["annee", "Num_Acc"])
             .groupby(["annee", "dep"]).size().rename("accidents_impliquant").reset_index())
        frames.append(n.assign(groupe=groupe))
    df = pd.concat(frames).merge(parc, on=["annee", "dep", "groupe"], how="right")
    df["accidents_impliquant"] = df["accidents_impliquant"].fillna(0).astype("int32")
    df["eff_accidents_10k_veh"] = df["accidents_impliquant"]
    df["taux_accidents_10k_veh"] = masque_seuil(
        pour_10k_vehicules(df["accidents_impliquant"], df["parc"].where(df["parc"] > 0)),
        df["eff_accidents_10k_veh"])
    return df


def build_s08(u: pd.DataFrame, acc: pd.DataFrame, pop_dep: pd.DataFrame,
              noms: dict[str, str]) -> pd.DataFrame:
    g = agg_usagers(u, ["annee", "dep"])
    a = agg_accidents(acc, ["annee", "dep"])
    df = a.merge(g, on=["annee", "dep"], how="outer").merge(
        pop_dep.drop(columns="metropole"), on=["annee", "dep"], how="left")
    df["nom_dep"] = df["dep"].map(noms)
    df["metropole"] = ~df["dep"].isin(C.DEP_OUTRE_MER)
    pop = df["population"]

    df["eff_victimes_100k"] = df["victimes"]
    df["taux_victimes_100k"] = masque_seuil(pour_100k(df["victimes"], pop), df["victimes"])
    df["eff_tues_million"] = df["tues"]
    df["taux_tues_million"] = masque_seuil(par_million(df["tues"], pop), df["tues"])
    df["eff_letalite"] = df["victimes"]
    df["taux_letalite"] = masque_seuil(letalite(df["tues"], df["victimes"]), df["victimes"])
    df["eff_gravite"] = df["victimes"]
    df["taux_gravite"] = masque_seuil(
        taux_gravite(df["tues"], df["hospitalises"], df["victimes"]), df["victimes"])
    return df.sort_values(["annee", "dep"]).reset_index(drop=True)


# --- Contrôles de cohérence (G4) -------------------------------------------

def controles_annuels(u: pd.DataFrame, acc: pd.DataFrame) -> pd.DataFrame:
    def bloc(uu, aa, perimetre):
        g = uu.groupby("annee").agg(
            usagers=("id_usager", "size"), victimes=("victime", "sum"), tues=("tue", "sum"),
            hospitalises=("hospitalise", "sum"), legers=("leger", "sum"),
            grav_manquante=("grav", lambda s: int(s.isna().sum())),
            en_fuite=("en_fuite", "sum"))
        g["accidents"] = aa.groupby("annee").size()
        g["letalite"] = letalite(g["tues"], g["victimes"]).round(2)
        return g.reset_index().assign(perimetre=perimetre)

    return pd.concat([bloc(u, acc, "France entière (métropole + outre-mer)"),
                      bloc(u[u["metropole"]], acc[acc["metropole"]], "France métropolitaine")],
                     ignore_index=True)
