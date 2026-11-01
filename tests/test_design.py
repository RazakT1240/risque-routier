"""Garde-fous de design vérifiés automatiquement (G9, G11)."""

import re
from pathlib import Path

from design import tokens
from design.theme import THEME

ROOT = Path(__file__).resolve().parents[1]
AUTORISES = {ROOT / "design" / "tokens.py", ROOT / "app" / "assets" / "custom.css"}
DOSSIERS = ["app", "design", "pipeline", "sandbox"]
# Bibliothèques tierces minifiées (ECharts) : hors du périmètre de G9
TIERS = ROOT / "app" / "assets" / "vendor"
# Hexadécimaux 3, 4, 6, 8 chiffres et fonctions de couleur rgb(), rgba(), hsl(), hsla()
HEX = re.compile(r"#(?:[0-9A-Fa-f]{8}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3,4})(?![0-9A-Za-z_-])"
                 r"|\b(?:rgba?|hsla?)\(", re.IGNORECASE)


def fichiers_source():
    for d in DOSSIERS:
        for p in (ROOT / d).rglob("*"):
            if (p.suffix in {".py", ".css", ".js"} and "__pycache__" not in p.parts
                    and TIERS not in p.parents):
                yield p


def test_aucun_hexadecimal_hors_fichiers_autorises():
    fautes = []
    for p in fichiers_source():
        if p in AUTORISES:
            continue
        for i, ligne in enumerate(p.read_text(encoding="utf-8").splitlines(), start=1):
            if HEX.search(ligne):
                fautes.append(f"{p.relative_to(ROOT)}:{i}: {ligne.strip()}")
    assert not fautes, "\n".join(fautes)


def test_tokens_complets_dans_les_deux_modes():
    assert tokens.LIGHT.keys() == tokens.DARK.keys()
    for scheme in ("light", "dark"):
        t = tokens.tokens(scheme)
        assert all(f"seq-{i}" in t for i in range(1, 6))


def test_css_reprend_les_tokens_du_mode_clair():
    css = (ROOT / "app" / "assets" / "custom.css").read_text(encoding="utf-8")
    racine = css.split("[data-mantine-color-scheme=\"dark\"]")[0]
    for nom, valeur in tokens.LIGHT.items():
        if nom == "on-image":
            continue
        assert f"--{nom}:{valeur}" in racine, nom


def test_css_reprend_les_tokens_du_mode_sombre():
    css = (ROOT / "app" / "assets" / "custom.css").read_text(encoding="utf-8")
    sombre = css.split("[data-mantine-color-scheme=\"dark\"]{")[1].split("}")[0]
    for nom, valeur in tokens.DARK.items():
        if nom == "on-image":
            continue
        assert f"--{nom}:{valeur}" in sombre, nom


def test_css_sequentielles_et_valeurs_partagees():
    css = (ROOT / "app" / "assets" / "custom.css").read_text(encoding="utf-8")
    racine, sombre = css.split("[data-mantine-color-scheme=\"dark\"]{", 1)
    sombre = sombre.split("}")[0]
    for i, (clair, nuit) in enumerate(zip(tokens.SEQ["light"], tokens.SEQ["dark"], strict=True),
                                       start=1):
        assert f"--seq-{i}:{clair}" in racine and f"--seq-{i}:{nuit}" in sombre
    r, g, b = tokens.HERO_VOILE_RGB
    a1, a2 = tokens.HERO_VOILE_OPACITES
    assert f"rgba({r},{g},{b},{str(a1).lstrip('0')})" in racine
    assert f"rgba({r},{g},{b},{str(a2).lstrip('0')})" in racine
    assert f"--shadow-hover:{tokens.SURVOL_OMBRE}" in racine
    for nom, px in (("sm", 6), ("md", 12), ("lg", 16)):
        assert tokens.RADIUS[nom] == px and f"--radius-{nom}:{px}px" in racine


def test_gammes_mantine_10_nuances():
    for nom, gamme in THEME["colors"].items():
        assert len(gamme) == 10, nom
