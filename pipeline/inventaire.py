"""Inventaire des fichiers bruts de data/ (phase 0).

Pour chaque fichier : nombre de lignes, colonnes, encodage, séparateur.
Puis vérifie les pièges listés dans LISEZMOI.txt. Lecture seule (G7).

Usage : python -m pipeline.inventaire   -> écrit reports/inventaire.md
"""

from __future__ import annotations

import gzip
import json
import logging
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORT = ROOT / "reports" / "inventaire.md"
ANNEES = range(2019, 2026)
TABLES = ("caract", "lieux", "vehicules", "usagers")
SAMPLE_BYTES = 2_000_000

log = logging.getLogger("inventaire")


def _open_bytes(path: Path) -> bytes:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rb") as f:
        return f.read(SAMPLE_BYTES)


def detect_encoding(sample: bytes) -> str:
    if sample.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    try:
        sample.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError as e:
        # Un caractère multi-octets peut être coupé en fin d'échantillon
        if e.start >= len(sample) - 4:
            return "utf-8"
        return "cp1252"


def detect_sep(sample: str) -> str:
    first = sample.splitlines()[0]
    return max((";", ",", "\t", "|"), key=first.count)


def read_csv_str(path: Path, sep: str, encoding: str) -> pd.DataFrame:
    return pd.read_csv(path, sep=sep, encoding=encoding, dtype=str, keep_default_na=False,
                       compression="infer", low_memory=False)


def inventory_csv(path: Path) -> tuple[dict, pd.DataFrame | None]:
    sample = _open_bytes(path)
    enc = detect_encoding(sample)
    sep = detect_sep(sample.decode(enc, errors="replace"))
    if "meteo_stations" in path.name:
        # 6,4 M lignes : on compte par morceaux sans garder le tableau
        n, cols = 0, None
        for chunk in pd.read_csv(path, sep=sep, encoding=enc, dtype=str, chunksize=500_000):
            cols = cols or list(chunk.columns)
            n += len(chunk)
        return {"fichier": path.relative_to(ROOT).as_posix(), "lignes": n, "colonnes": cols,
                "encodage": enc, "sep": sep}, None
    df = read_csv_str(path, sep, enc)
    return {"fichier": path.relative_to(ROOT).as_posix(), "lignes": len(df),
            "colonnes": list(df.columns), "encodage": enc, "sep": sep}, df


def inventory_xlsx(path: Path) -> dict:
    wb = load_workbook(path, read_only=True)
    sheets = wb.sheetnames
    info = {"fichier": path.relative_to(ROOT).as_posix(), "onglets": len(sheets),
            "premier": sheets[0], "dernier": sheets[-1], "lignes_par_onglet": {}}
    for name in sheets:
        info["lignes_par_onglet"][name] = wb[name].max_row
    wb.close()
    return info


def inventory_geojson(path: Path) -> dict:
    gj = json.loads(path.read_text(encoding="utf-8"))
    codes = sorted(f["properties"]["code"] for f in gj["features"])
    return {"fichier": path.relative_to(ROOT).as_posix(), "entites": len(codes),
            "codes": codes, "proprietes": list(gj["features"][0]["properties"])}


def check(label: str, ok: bool, detail: str = "") -> dict:
    return {"piege": label, "ok": ok, "detail": detail}


def check_baac(frames: dict) -> list[dict]:
    out = []
    key22 = frames[("caract", 2022)].columns[0]
    out.append(check("2022 : clé `Accident_Id` dans caract", key22 == "Accident_Id",
                     f"1re colonne = `{key22}`"))
    others22 = {t: frames[(t, 2022)].columns[0] for t in ("lieux", "vehicules", "usagers")}
    out.append(check("2022 : `Num_Acc` dans les autres tables",
                     all(c == "Num_Acc" for c in others22.values()), str(others22)))

    for y in ANNEES:
        has = "id_usager" in frames[("usagers", y)].columns
        expected = y >= 2021
        out.append(check(f"{y} : `id_usager` {'présent' if expected else 'absent'} dans usagers",
                         has == expected, f"présent={has}"))

    cols25 = list(frames[("vehicules", 2025)].columns)
    broken = [c for c in cols25 if c != c.strip()]
    stripped = [c.strip() for c in cols25]
    cols24 = list(frames[("vehicules", 2024)].columns)
    out.append(check("2025 : en-tête de vehicules coupé (retour à la ligne dans un nom)",
                     bool(broken), f"noms bruts concernés : {[repr(c) for c in broken]}"))
    out.append(check("2025 : après strip, 11 colonnes identiques à 2024",
                     len(stripped) == 11 and stripped == cols24, f"{len(stripped)} colonnes"))

    for y in ANNEES:
        dep = frames[("caract", y)]["dep"]
        short = dep[dep.str.len() == 1]
        out.append(check(f"{y} : codes `dep` à 1 caractère (sans zéro initial)", True,
                         f"{len(short)} lignes ({', '.join(sorted(short.unique())[:5])})"
                         if len(short) else "aucun"))

    for y in ANNEES:
        lieux = frames[("lieux", y)]
        dup = lieux["Num_Acc"].duplicated().sum()
        out.append(check(f"{y} : doublons de `Num_Acc` dans lieux", True,
                         f"{dup} lignes en double sur {len(lieux)}"))

    for y in ANNEES:
        c = frames[("caract", y)]
        key = c.columns[0]
        out.append(check(f"{y} : `{key}` unique dans caract", c[key].is_unique,
                         f"{len(c)} accidents"))
        lat_virgule = c["lat"].str.contains(",", regex=False).mean()
        out.append(check(f"{y} : lat en décimale virgule", lat_virgule > 0.99,
                         f"{lat_virgule:.1%} des lignes"))

    # Pièges non listés dans LISEZMOI : espaces en tête et "N/A"
    for y in ANNEES:
        lead, na = {}, {}
        for t in TABLES:
            df = frames[(t, y)]
            lead[t] = int(sum(df[c].str.startswith(" ").sum() for c in df.columns))
            na[t] = int(sum((df[c] == "N/A").sum() for c in df.columns))
        out.append(check(f"{y} : valeurs avec espace en tête (ex. ` -1`)", True, str(lead)))
        out.append(check(f"{y} : valeurs `N/A` littérales", True, str(na)))

    for y in ANNEES:
        g = frames[("usagers", y)]["grav"].str.strip().value_counts().to_dict()
        out.append(check(f"{y} : valeurs de `grav`", True, str(dict(sorted(g.items())))))
    return out


def check_others(meteo: pd.DataFrame, sdes: pd.DataFrame, geo: dict) -> list[dict]:
    out = []
    deps = set(meteo["dep"])
    out.append(check("Météo : Corse codée `20`", "20" in deps and not {"2A", "2B"} & deps,
                     f"20 présent={'20' in deps}, 2A/2B présents={sorted({'2A','2B'} & deps)}"))
    out.append(check("Météo : Mayotte (976) absente", "976" not in deps,
                     f"{len(deps)} départements"))
    out.append(check("Météo : période couverte", True,
                     f"{meteo['date'].min()} → {meteo['date'].max()}"))
    out.append(check("SDES : présence de `dep=00`", (sdes["dep"] == "00").any(),
                     f"{(sdes['dep'] == '00').sum()} lignes"))
    groupes = sorted(sdes["groupe"].unique())
    out.append(check("SDES : groupes = VP, VUL, PL, TCP (pas de 2RM)",
                     set(groupes) <= {"VP", "VUL", "PL", "TCP"}, str(groupes)))
    out.append(check("SDES : catégories", True, str(sorted(sdes["categorie"].unique()))))
    g = geo["departements-version-simplifiee.geojson"]
    out.append(check("GeoJSON simplifié : 96 départements, clé `code`",
                     g["entites"] == 96 and "code" in g["proprietes"],
                     f"{g['entites']} entités, propriétés {g['proprietes']}"))
    return out


def check_insee(path: Path) -> list[dict]:
    """Structure d'un onglet : en-têtes lignes 1-5, données à partir de la ligne 6."""
    out = []
    wb = load_workbook(path, read_only=True)
    for y in ANNEES:
        name = str(y)
        if name not in wb.sheetnames:
            out.append(check(f"INSEE : onglet {y} présent", False, "absent"))
            continue
        rows = list(wb[name].iter_rows(min_row=1, max_row=120, values_only=True))
        blocs = [v for v in rows[3] if v]
        classes = [v for v in rows[4] if v]
        data = [r for r in rows[5:] if r[0] is not None]
        int_codes = [r[0] for r in data if isinstance(r[0], int)]
        aggregats = [r[0] for r in data if isinstance(r[0], str) and not r[0][:1].isdigit()
                     and r[0] not in ("2A", "2B")]
        out.append(check(f"INSEE {y} : blocs ligne 4 / classes ligne 5", True,
                         f"blocs={blocs[:3]}, {len(classes)} classes, 1re=`{classes[0]}`, "
                         f"dernière=`{classes[-1]}`"))
        out.append(check(f"INSEE {y} : codes entiers / agrégats", True,
                         f"entiers={int_codes[:5]}, agrégats={aggregats[:4]}, {len(data)} lignes"))
    wb.close()
    return out


def to_markdown(files: list[dict], checks: list[dict]) -> str:
    lines = ["# Inventaire des données brutes", "",
             "Généré par `python -m pipeline.inventaire`. Lecture seule de `data/`.", "",
             "## Fichiers CSV", "", "| Fichier | Lignes | Col. | Encodage | Sép. | Colonnes |",
             "| --- | ---: | ---: | --- | --- | --- |"]
    for f in files:
        if "lignes" in f:
            cols = ", ".join(repr(c) if c != c.strip() else c for c in f["colonnes"])
            lines.append(f"| `{f['fichier']}` | {f['lignes']} | {len(f['colonnes'])} | "
                         f"{f['encodage']} | `{f['sep']}` | {cols} |")
    lines += ["", "## Fichiers Excel et GeoJSON", ""]
    for f in files:
        if "onglets" in f:
            lines.append(f"- `{f['fichier']}` : {f['onglets']} onglets ({f['premier']} → "
                         f"{f['dernier']}), lignes/onglet 2019–2025 : "
                         + ", ".join(f"{k}={v}" for k, v in f["lignes_par_onglet"].items()
                                     if k.isdigit() and 2019 <= int(k) <= 2025))
        elif "entites" in f:
            lines.append(f"- `{f['fichier']}` : {f['entites']} entités, propriétés "
                         f"{f['proprietes']}")
    lines += ["", "## Pièges vérifiés", "", "| Contrôle | Statut | Détail |", "| --- | --- | --- |"]
    for c in checks:
        lines.append(f"| {c['piege']} | {'OK' if c['ok'] else '**ÉCART**'} | "
                     f"{c['detail'].replace('|', '/')} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    files, frames = [], {}
    for y in ANNEES:
        for t in TABLES:
            path = DATA / "baac" / str(y) / f"{t}-{y}.csv"
            log.info("lecture %s", path.name)
            info, df = inventory_csv(path)
            files.append(info)
            frames[(t, y)] = df
    others = {}
    for path in sorted((DATA / "meteo").glob("*")) + sorted((DATA / "sdes").glob("*.csv")):
        log.info("lecture %s", path.name)
        info, df = inventory_csv(path)
        files.append(info)
        others[path.name] = df
    geo = {}
    for path in sorted((DATA / "geo").glob("*.geojson")):
        info = inventory_geojson(path)
        files.append(info)
        geo[path.name] = info
    for path in sorted((DATA / "insee").glob("*.xlsx")):
        log.info("lecture %s", path.name)
        files.append(inventory_xlsx(path))

    checks = check_baac(frames)
    checks += check_others(others["meteo_dep_jour_2019_2025.csv"],
                           others["sdes_parc_vehicules_dep_2019_2026.csv"], geo)
    checks += check_insee(DATA / "insee" / "insee_estim-pop-dep-sexe-aq-1975-2026.xlsx")

    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(to_markdown(files, checks), encoding="utf-8")
    n_bad = sum(not c["ok"] for c in checks)
    log.info("%d contrôles, %d écart(s) -> %s", len(checks), n_bad, REPORT.relative_to(ROOT))


if __name__ == "__main__":
    main()
