"""Contrats de données sur data/processed/ (CLAUDE.md, phase 1)."""

import json

import pandas as pd
import pytest

from pipeline import config as C

pytestmark = pytest.mark.skipif(not (C.PROCESSED / "usagers_enrichis.parquet").exists(),
                                reason="lancer d'abord `python -m pipeline.run`")

DEP_REGEX = r"0[1-9]|1\d|[3-8]\d|9[0-5]|2[1-9]|2[AB]|97[1-8]|98[678]"
AGREGATS = ["pop_dep", "s02_gravite", "s02_accidents", "s03_vma", "s03_lum", "s03_obs",
            "s04_age", "s04_casque", "s05_heatmap", "ind_parc", "s08_donnees", "s03_matrice"]


def read(name: str) -> pd.DataFrame:
    return pd.read_parquet(C.PROCESSED / f"{name}.parquet")


@pytest.fixture(scope="module")
def usagers():
    return read("usagers_enrichis")


@pytest.fixture(scope="module")
def accidents():
    return read("accidents")


def test_num_acc_unique_dans_accidents(accidents):
    # lieux dédoublonné : une seule ligne par accident après jointure
    assert accidents["Num_Acc"].is_unique


def test_cle_usager_unique(usagers):
    assert not usagers.duplicated(["Num_Acc", "id_usager"]).any()


def test_grav_dans_codes(usagers):
    assert set(usagers["grav"].dropna().unique()) <= {1, 2, 3, 4}


def test_grav_manquante_seulement_usagers_en_fuite_periode(usagers):
    assert usagers.loc[usagers["grav"].isna(), "annee"].min() >= 2021


def test_departements_format(accidents, usagers):
    for df in (accidents, usagers):
        assert df["dep"].astype(str).str.fullmatch(DEP_REGEX).all()


def test_toutes_les_annees(accidents, usagers):
    assert sorted(accidents["annee"].unique()) == C.ANNEES
    assert sorted(usagers["annee"].unique()) == C.ANNEES


def test_usagers_rattaches_a_un_accident(usagers, accidents):
    assert usagers["Num_Acc"].isin(accidents["Num_Acc"]).all()


def test_population_positive_par_dep_annee():
    pop = read("pop_dep")
    assert (pop["population"] > 0).all()
    met = pop[pop["metropole"]]
    assert met.groupby("annee")["dep"].nunique().eq(96).all()
    assert sorted(met["annee"].unique()) == C.ANNEES


def test_population_couvre_departements_baac(accidents):
    pop = read("pop_dep")
    met_baac = set(accidents.loc[accidents["metropole"], "dep"])
    assert met_baac <= set(pop["dep"])


def test_aucun_taux_sous_le_seuil():
    for path in C.PROCESSED.glob("*.parquet"):
        df = pd.read_parquet(path)
        for col in [c for c in df.columns if c.startswith("taux_")]:
            eff = "eff_" + col.removeprefix("taux_")
            assert eff in df.columns, f"{path.name}: {col} sans {eff}"
            shown = df[col].notna()
            assert (df.loc[shown, eff] >= C.SEUIL_EFFECTIF).all(), f"{path.name}: {col}"


def test_vma_valides(usagers):
    assert set(usagers["vma"].dropna().unique()) <= C.VMA_VALIDES


def test_age_borne(usagers):
    assert usagers["age"].dropna().between(C.AGE_MIN, C.AGE_MAX).all()


def test_type_usager_complet(usagers):
    assert usagers["type_usager"].notna().all()
    assert (usagers.loc[usagers["catu"] == 3, "type_usager"] == "Piéton").all()


def test_agregats_coherents_avec_usagers(usagers):
    g = read("s02_gravite")
    met = usagers[usagers["metropole"]]
    assert g["tues"].sum() == met["tue"].sum()
    assert g["victimes"].sum() == met["victime"].sum()


def test_meteo_corse_dupliquee():
    m = read("meteo_dep_jour")
    deps = set(m["dep"])
    assert {"2A", "2B"} <= deps and "20" not in deps


@pytest.mark.parametrize("name", AGREGATS)
def test_agregats_annees_et_departements(name):
    df = read(name)
    assert sorted(df["annee"].unique()) == C.ANNEES
    assert df["dep"].astype(str).str.fullmatch(DEP_REGEX).all()


def test_departements_carte_couverts(accidents):
    gj = json.loads(C.RAW_GEO.read_text(encoding="utf-8"))
    codes = {f["properties"]["code"] for f in gj["features"]}
    assert set(accidents.loc[accidents["metropole"], "dep"]) <= codes


def test_aucun_usager_perdu(usagers):
    n_bruts = 0
    for a in C.ANNEES:
        path = C.RAW_BAAC / str(a) / f"usagers-{a}.csv"
        n_bruts += len(pd.read_csv(path, sep=";", usecols=[0], dtype=str))
    assert n_bruts == len(usagers)


def test_population_fine_positive():
    pop = read("expo_population")
    assert (pop["population"] >= 0).all()
    assert pop.groupby(["annee", "dep"])["population"].sum().gt(0).all()
    assert pop["classe_age"].nunique() == len(C.CLASSES_AGE)


def test_totaux_tues_coherents_entre_scenes():
    ref = read("s02_gravite")["tues"].sum()
    for name in ("s03_vma", "s03_lum", "s03_obs", "s04_age", "s05_heatmap"):
        assert read(name)["tues"].sum() == ref, name


def test_territoires_cumul():
    t = read("ind_territoires")
    cumul = t[t["periode"] == f"{C.ANNEES[0]}–{C.ANNEES[-1]}"]
    assert len(cumul) == 96
    assert cumul["taux_victimes_100k"].notna().all()


def test_casque_trois_modalites():
    c = read("s04_casque")
    assert set(c["casque"].astype(str)) <= set(C.CASQUE_ORDRE)


def test_modeles_json():
    for name in ("meteo.json", "simulateur.json"):
        obj = json.loads((C.MODELS / name).read_text(encoding="utf-8"))
        assert obj["n_obs"] > 0


def test_boites_age():
    b = read("s04_age_box")
    assert (b["n"] >= C.SEUIL_EFFECTIF).all()
    assert ((b["bas"] <= b["q1"]) & (b["q1"] <= b["mediane"]) & (b["mediane"] <= b["q3"])
            & (b["q3"] <= b["haut"])).all()
