"""Formatage des nombres à la française (CLAUDE.md §9) — fonctions uniques.

Milliers : espace fine insécable ; décimales : virgule ; « % » précédé d'une espace insécable.
Valeur manquante : « — » (G1).
"""

from __future__ import annotations

import math

NA = "—"
MILLIERS = " "     # espace fine insécable
INSECABLE = " "
MOINS = "−"        # vrai signe moins


def _manquant(x) -> bool:
    return x is None or (isinstance(x, float) and math.isnan(x))


def fmt_number(x, decimals: int = 0, signe: bool = False) -> str:
    if _manquant(x):
        return NA
    txt = f"{abs(x):,.{decimals}f}".replace(",", MILLIERS).replace(".", ",")
    if x < 0 and txt.strip("0, "):
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


def delta(valeur, reference, libelle: str, plus_est_mauvais: bool = True,
          decimals: int = 1) -> dict:
    """Variation affichable : flèche ▲▼ + couleur selon le sens POUR L'ASSUREUR (DESIGN §2.2)."""
    v = variation_pct(valeur, reference)
    if v is None:
        return {"texte": f"{NA} vs {libelle}", "sens": "neutre"}
    arrondi = round(v, decimals)
    if arrondi == 0:
        return {"texte": f"= {fmt_pct(0, decimals)} vs {libelle}", "sens": "neutre"}
    fleche = "▲" if v > 0 else "▼"
    mauvais = (v > 0) == plus_est_mauvais
    return {"texte": f"{fleche} {fmt_pct(v, decimals, signe=True)} vs {libelle}",
            "sens": "defavorable" if mauvais else "favorable"}
