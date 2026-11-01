"""Formules uniques d'indicateurs (BRIEF §3) et seuil G6, réutilisées par l'app."""

import pandas as pd

from pipeline import config as C
from pipeline import indicators as I


def test_masque_seuil_exact():
    taux = pd.Series([1.0, 2.0, 3.0])
    eff = pd.Series([C.SEUIL_EFFECTIF - 1, C.SEUIL_EFFECTIF, C.SEUIL_EFFECTIF + 1])
    out = I.masque_seuil(taux, eff)
    assert out.isna().tolist() == [True, False, False]


def test_seuil_unique_constante():
    assert C.SEUIL_EFFECTIF == 30


def test_formules():
    assert I.letalite(5, 100) == 5
    assert I.taux_gravite(5, 15, 100) == 20
    assert I.pour_100k(10, 1_000_000) == 1
    assert I.par_million(3, 1_000_000) == 3
    assert I.pour_10k_vehicules(20, 100_000) == 2
    assert I.base_100(80, 100) == 80
