"""`python -m pipeline.run` : reconstruit data/processed/ et reports/controles.md."""

from __future__ import annotations

import logging
import time

import pandas as pd

from pipeline import config as C
from pipeline import indicators, load, models, prepare

log = logging.getLogger("pipeline")

# G4 : écart relatif au-delà duquel une année (hors 2020) est jugée anormale
ECART_MAX_TUES = 0.15


def _write(df: pd.DataFrame, name: str) -> None:
    path = C.PROCESSED / f"{name}.parquet"
    df.to_parquet(path, index=False)
    log.info("  %-28s %9d lignes", path.name, len(df))


def write_controles(ctrl: pd.DataFrame, meteo_fit: dict, simu_fit: dict) -> None:
    lignes = [
        "# Contrôles de cohérence (G4)", "",
        "Généré par `python -m pipeline.run`. À comparer aux bilans ONISR de chaque année.",
        "", "Définitions : victime = tué + blessé hospitalisé + blessé léger ; tué = décès dans "
        "les 30 jours ; `grav manquante` = gravité non renseignée (usagers en fuite) ; "
        "`en fuite` = usager à partir de 2021 sans sexe ni année de naissance.", "",
    ]
    cols = ["annee", "accidents", "usagers", "victimes", "tues", "hospitalises", "legers",
            "letalite", "grav_manquante", "en_fuite"]
    titres = ["Année", "Accidents", "Usagers", "Victimes", "Tués", "Hospitalisés", "Légers",
              "Létalité (tués/100 vict.)", "Grav. manquante", "En fuite"]
    for perimetre, bloc in ctrl.groupby("perimetre", sort=False):
        lignes += [f"## {perimetre}", "", "| " + " | ".join(titres) + " |",
                   "|" + " ---: |" * len(titres)]
        for _, r in bloc.iterrows():
            lignes.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
        lignes.append("")
    met = ctrl[ctrl["perimetre"] == "France métropolitaine"].set_index("annee")["tues"]
    hors2020 = met.drop(2020)
    lignes += ["## Stabilité des tués (métropole, hors 2020)", "",
               f"Médiane : {hors2020.median():.0f} ; écart max toléré : "
               f"{ECART_MAX_TUES:.0%}.", ""]
    for a, v in met.items():
        lignes.append(f"- {a} : {v} ({(v / hors2020.median() - 1):+.1%})")
    lignes += ["", "## Modèles", "",
               f"- Météo : {meteo_fit['n_obs']} département-jours, dispersion "
               f"{meteo_fit['dispersion']:.2f}.",
               f"- Simulateur : {simu_fit['n_obs']} usagers, taux observé de blessure grave "
               f"{simu_fit['taux_observe']:.4f}.", ""]
    (C.REPORTS / "controles.md").write_text("\n".join(lignes), encoding="utf-8")


def check_stabilite(ctrl: pd.DataFrame) -> None:
    met = ctrl[ctrl["perimetre"] == "France métropolitaine"].set_index("annee")["tues"]
    hors2020 = met.drop(2020)
    ecarts = (hors2020 / hors2020.median() - 1).abs()
    anormales = ecarts[ecarts > ECART_MAX_TUES]
    if len(anormales):
        raise RuntimeError(f"G4 : années anormales pour les tués : {anormales.to_dict()}")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s",
                        datefmt="%H:%M:%S")
    t0 = time.perf_counter()
    C.PROCESSED.mkdir(parents=True, exist_ok=True)
    C.REPORTS.mkdir(exist_ok=True)

    log.info("1/5 lecture")
    raw = {t: load.load_baac_all(t) for t in C.TABLES_BAAC}
    meteo = prepare.prepare_meteo(load.load_meteo())
    pop = prepare.build_expo_population(load.load_insee())
    parc = prepare.build_expo_parc(load.load_sdes())
    noms = load.load_noms_dep()

    log.info("2/5 préparation")
    caract_e = prepare.enrich_caract(raw["caract"], raw["lieux"], meteo)
    usagers = prepare.build_usagers_enrichis(caract_e, raw["vehicules"], raw["usagers"])
    accidents = prepare.build_accidents(caract_e, usagers)

    log.info("3/5 contrôles G4")
    ctrl = indicators.controles_annuels(usagers, accidents)
    check_stabilite(ctrl)

    log.info("4/5 écriture des Parquet")
    _write(usagers, "usagers_enrichis")
    _write(accidents, "accidents")
    _write(pop, "expo_population")
    _write(parc, "expo_parc")
    _write(meteo, "meteo_dep_jour")
    for name, df in indicators.build_scenes(usagers, accidents, pop, parc, raw["vehicules"],
                                            noms).items():
        _write(df, name)

    log.info("5/5 modèles")
    meteo_fit = models.fit_meteo(accidents, meteo)
    simu_fit = models.fit_simulateur(usagers)
    write_controles(ctrl, meteo_fit, simu_fit)
    log.info("terminé en %.0f s", time.perf_counter() - t0)


if __name__ == "__main__":
    main()
