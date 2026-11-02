"""Formatage des nombres à la française (CLAUDE.md §9) — fonctions uniques.

Milliers : espace fine insécable ; décimales : virgule ; « % » précédé d'une espace insécable.
Valeur manquante : « — » (G1).
"""

from __future__ import annotations

import math

from app import i18n

NA = "—"
MILLIERS = "\u00a0"     # espace insécable (l'espace fine U+202F est quasi invisible)
INSECABLE = "\u00a0"
MOINS = "\u2212"        # vrai signe moins


def _manquant(x) -> bool:
    if x is None or isinstance(x, str):
        return True
    try:
        return bool(math.isnan(float(x)))
    except (TypeError, ValueError):
        return True


def fmt_number(x, decimals: int = 0, signe: bool = False, milliers: str = MILLIERS) -> str:
    """Format français par défaut ; anglais (virgule milliers, point décimal) si langue=en.
    `milliers=INSECABLE` pour les très grands corps (l'espace fine y devient invisible)."""
    if _manquant(x):
        return NA
    if i18n.langue() == "en":
        txt = f"{abs(x):,.{decimals}f}"                 # 1,234.5
        reste = txt.strip("0.,")
    else:
        txt = f"{abs(x):,.{decimals}f}".replace(",", milliers).replace(".", ",")
        reste = txt.strip("0," + MILLIERS + INSECABLE)
    if x < 0 and reste:
        return MOINS + txt
    if signe and x > 0:
        return "+" + txt
    return txt


def fmt_pct(x, decimals: int = 1, signe: bool = False) -> str:
    if _manquant(x):
        return NA
    # Anglais : pas d'espace avant « % » (12.4%) ; français : espace insécable (12,4 %).
    sep = "" if i18n.langue() == "en" else INSECABLE
    return f"{fmt_number(x, decimals, signe)}{sep}%"


def fmt_ratio(x, decimals: int = 2) -> str:
    """Risque relatif / rapport : « × 1,32 »."""
    if _manquant(x):
        return NA
    return f"×{INSECABLE}{fmt_number(x, decimals)}"


def variation_pct(valeur, reference):
    if _manquant(valeur) or _manquant(reference) or reference == 0:
        return None
    return (valeur / reference - 1) * 100


def delta_points(valeur, reference, libelle: str, plus_est_mauvais: bool | None = None,
                 decimals: int = 1) -> dict:
    """Variation d'une part ou d'un taux pour 100, en points (« ▲ +0,8 pt vs 2024 »)."""
    if _manquant(valeur) or _manquant(reference):
        return {"texte": f"{NA} vs {libelle}", "sens": "neutre"}
    v = round(valeur - reference, decimals)
    if v == 0:
        return {"texte": f"= {fmt_number(0, decimals)}{INSECABLE}pt vs {libelle}",
                "sens": "neutre"}
    fleche = "▲" if v > 0 else "▼"
    texte = f"{fleche} {fmt_number(v, decimals, signe=True)}{INSECABLE}pt vs {libelle}"
    if plus_est_mauvais is None:
        return {"texte": texte, "sens": "neutre"}
    return {"texte": texte, "sens": "defavorable" if (v > 0) == plus_est_mauvais else "favorable"}


def delta(valeur, reference, libelle: str, plus_est_mauvais: bool | None = True,
          decimals: int = 1) -> dict:
    """Variation affichable : flèche ▲▼ + couleur selon le sens POUR L'ASSUREUR (DESIGN §2.2)."""
    v = variation_pct(valeur, reference)
    if v is None:
        return {"texte": f"{NA} vs {libelle}", "sens": "neutre"}
    arrondi = round(v, decimals)
    if arrondi == 0:
        return {"texte": f"= {fmt_pct(0, decimals)} vs {libelle}", "sens": "neutre"}
    fleche = "▲" if v > 0 else "▼"
    if plus_est_mauvais is None:          # part ou structure : ni bonne ni mauvaise
        return {"texte": f"{fleche} {fmt_pct(v, decimals, signe=True)} vs {libelle}",
                "sens": "neutre"}
    mauvais = (v > 0) == plus_est_mauvais
    return {"texte": f"{fleche} {fmt_pct(v, decimals, signe=True)} vs {libelle}",
            "sens": "defavorable" if mauvais else "favorable"}
