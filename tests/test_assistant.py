"""Contrats de l'assistant RAG : fiches ancrées aux données, récupération pertinente (G1)."""

from __future__ import annotations

from app import assistant as A
from app import data_access as da
from app.components.format import fmt_number


def test_index_construit_des_fiches():
    A._assurer_index()
    assert len(A._FICHES) > 50
    # Chaque fiche porte une réponse, une source et une scène existante
    chemins = {"/", "/vue-ensemble", "/paradoxe", "/qui", "/ou-quand", "/evolution",
               "/simulateur", "/methode"}
    for f in A._FICHES:
        assert f.reponse and f.source and f.scene_path in chemins


def test_reponse_tues_annee_vient_des_donnees():
    """Le chiffre affiché par l'assistant doit être exactement celui des Parquet (G1)."""
    g = da.table("s02_gravite")
    attendu = int(g[g["annee"] == da.DERNIERE_ANNEE]["tues"].sum())
    fiches = A.rechercher(f"combien de tués en {da.DERNIERE_ANNEE} ?")
    assert fiches, "aucune fiche récupérée"
    assert fmt_number(attendu) in fiches[0]["reponse"]


def test_recuperation_pertinente():
    cas = {
        "la pluie provoque-t-elle plus d'accidents ?": "meteo-pluie",
        "quel département est le plus risqué ?": "terr-palmares",
        "risque des deux-roues": "mode-2RM",
        "d'où viennent les données ?": "meth-sources",
    }
    for question, cle in cas.items():
        fiches = A.rechercher(question)
        assert fiches and fiches[0]["cle"] == cle, (question, fiches[:1])


def test_question_vide_ou_hors_sujet():
    assert A.rechercher("") == []
    assert A.rechercher("xyzzy qwerty") == []
