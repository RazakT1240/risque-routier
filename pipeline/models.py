"""Modèles statistiques -> coefficients JSON (BRIEF §5 scènes 05 et 07).

- Météo : GLM Poisson (quasi-Poisson : échelle estimée par le chi² de Pearson, pour des IC
  honnêtes en cas de surdispersion) sur le nombre d'accidents par département-jour.
- Simulateur : régression logistique P(blessure grave | usager impliqué).
"""

from __future__ import annotations

import json
import logging
import math

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from pipeline import config as cfg  # pas « C » : nom réservé aux formules patsy

log = logging.getLogger(__name__)
Z95 = 1.959963984540054


def _write_json(obj: dict, name: str) -> None:
    cfg.MODELS.mkdir(parents=True, exist_ok=True)
    (cfg.MODELS / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def fit_meteo(acc: pd.DataFrame, meteo: pd.DataFrame) -> dict:
    deps = sorted(acc.loc[acc["metropole"], "dep"].unique())
    grid = meteo[meteo["dep"].isin(deps)][["dep", "date", "meteo_cat", "premiere_pluie"]].copy()
    n = acc[acc["metropole"]].groupby(["dep", "date"]).size().rename("nb_accidents")
    df = grid.merge(n.reset_index(), on=["dep", "date"], how="left")
    df["nb_accidents"] = df["nb_accidents"].fillna(0).astype(int)
    df["mois"] = df["date"].dt.month
    df["annee"] = df["date"].dt.year
    df["jour_semaine"] = df["date"].dt.dayofweek

    formule = ("nb_accidents ~ C(meteo_cat, Treatment('sec')) + premiere_pluie + C(dep)"
               " + C(mois) + C(annee) + C(jour_semaine)")
    log.info("GLM météo : %d département-jours", len(df))
    res = smf.glm(formule, data=df, family=sm.families.Poisson()).fit(scale="X2")

    effets = {"sec": {"rr": 1.0, "ic_bas": 1.0, "ic_haut": 1.0, "reference": True,
                      "n_jours": int((df["meteo_cat"] == "sec").sum())}}
    for cat in cfg.METEO_CAT_ORDRE[1:]:
        effets[cat] = _effet(res, f"C(meteo_cat, Treatment('sec'))[T.{cat}]")
        effets[cat]["n_jours"] = int((df["meteo_cat"] == cat).sum())
    effets["premiere_pluie"] = _effet(res, "premiere_pluie")
    effets["premiere_pluie"]["n_jours"] = int(df["premiere_pluie"].sum())

    out = {"modele": "GLM Poisson, échelle de Pearson (quasi-Poisson)", "formule": formule,
           "periode": f"{cfg.ANNEES[0]}-{cfg.ANNEES[-1]}", "perimetre": "France métropolitaine",
           "n_obs": int(res.nobs), "dispersion": float(res.scale), "effets": effets,
           "lecture": "rr = risque relatif d'accident un jour de la catégorie vs un jour sec, "
                      "à département, mois, année et jour de semaine égaux ; premiere_pluie = "
                      "surcroît d'un 1er jour de pluie après au moins 7 jours secs."}
    _write_json(out, "meteo.json")
    return out


def _effet(res, nom: str) -> dict:
    b, se = float(res.params[nom]), float(res.bse[nom])
    return {"coef": b, "se": se, "p": float(res.pvalues[nom]), "rr": math.exp(b),
            "ic_bas": math.exp(b - Z95 * se), "ic_haut": math.exp(b + Z95 * se)}


SIMU_VARS = {
    "type_usager": "Voiture", "classe_age": "45-49", "sexe_lib": "Homme",
    "agg_lib": "En agglomération", "nuit": "Non", "meteo_cat": "sec", "catr_groupe": "Communale",
}


def fit_simulateur(u: pd.DataFrame) -> dict:
    df = u[u["metropole"]].copy()
    df["nuit"] = df["nuit"].map({True: "Oui", False: "Non"})
    cols = list(SIMU_VARS)
    df = df[[*cols, "grave"]].dropna()
    for c in cols:
        df[c] = df[c].astype(str)
    log.info("Logistique simulateur : %d usagers", len(df))

    blocs, noms = [], []
    niveaux = {}
    for var, ref in SIMU_VARS.items():
        lv = sorted(df[var].unique(), key=_ordre(var))
        if ref not in lv:
            raise ValueError(f"référence {ref!r} absente pour {var}")
        niveaux[var] = lv
        for niv in lv:
            if niv != ref:
                blocs.append((df[var] == niv).to_numpy(np.float64))
                noms.append((var, niv))
    X = np.column_stack([np.ones(len(df)), *blocs])
    y = df["grave"].astype(int).to_numpy()
    res = sm.GLM(y, X, family=sm.families.Binomial()).fit()

    x_moy = X.mean(axis=0)
    eta_moy = float(x_moy @ res.params)
    coefs = {var: {SIMU_VARS[var]: {"coef": 0.0, "se": 0.0, "moyenne": None, "reference": True}}
             for var in SIMU_VARS}
    for k, (var, niv) in enumerate(noms, start=1):
        coefs[var][niv] = {"coef": float(res.params[k]), "se": float(res.bse[k]),
                           "moyenne": float(x_moy[k])}
    for var in SIMU_VARS:
        ref = SIMU_VARS[var]
        coefs[var][ref]["moyenne"] = float((df[var] == ref).mean())

    out = {"modele": "Régression logistique (GLM binomial, lien logit)",
           "cible": "grave = tué ou blessé hospitalisé, parmi les usagers impliqués",
           "periode": f"{cfg.ANNEES[0]}-{cfg.ANNEES[-1]}", "perimetre": "France métropolitaine",
           "n_obs": int(res.nobs), "taux_observe": float(y.mean()),
           "intercept": float(res.params[0]), "eta_profil_moyen": eta_moy,
           "proba_profil_moyen": 1 / (1 + math.exp(-eta_moy)),
           "niveaux": niveaux, "references": SIMU_VARS, "coefs": coefs,
           "lecture": "eta = intercept + somme des coefs des modalités choisies ; "
                      "probabilité = 1 / (1 + exp(-eta)) ; rapport de cotes vs profil moyen = "
                      "exp(eta - eta_profil_moyen)."}
    _write_json(out, "simulateur.json")
    return out


def _ordre(var: str):
    ordres = {"type_usager": cfg.TYPE_USAGER_ORDRE, "classe_age": cfg.CLASSES_AGE,
              "catr_groupe": cfg.CATR_GROUPE_ORDRE, "meteo_cat": cfg.METEO_CAT_ORDRE}
    if var in ordres:
        return ordres[var].index
    return lambda v: v
