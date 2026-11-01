"""Formatage des nombres à la française (CLAUDE.md §9) — fonctions uniques.

Milliers : espace fine insécable ; décimales : virgule ; « % » précédé d'une espace insécable.
Valeur manquante : « — » (G1).
"""

from __future__ import annotations

import math

NA = "—"
MILLIERS = "\u202f"     # espace fine insécable
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
    """`milliers=INSECABLE` pour les très grands corps (l'espace fine y devient invisible)."""
    if _manquant(x):
        return NA
    txt = f"{abs(x):,.{decimals}f}".replace(",", milliers).replace(".", ",")
    if x < 0 and txt.strip("0," + MILLIERS + INSECABLE):
        return MOINS + txt
    if signe and x > 0:
        return "+" + txt
    return txt


def fmt_pct(x, decimals: int = 1, signe: bool = False) -> str:
    if _manquant(x):
        return NA
    return f"{fmt_number(x, decimals, signe)}{INSECABLE}%"


def fmt_ratio(x, decimals: int = 2) -> str:
    """Risque relatif / rapport : « × 1,32 »."""
    if _manquant(x):
        return NA
    return f"×{INSECABLE}{fmt_number(x, decimals)}"


def variation_pct(valeur, reference):
    if _manquant(valeur) or _manquant(reference) or reference == 0:
        return None
    return (valeur / reference - 1) * 100


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
