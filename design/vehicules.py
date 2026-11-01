"""Illustrations d'usagers de la route en volume (isométrique « 3D plat »).

Images générées (aucun droit tiers), sans gradient décoratif (G11) : le relief vient de trois
tons par volume (dessus clair / côté / face ombrée), lus dans tokens.VEHICULE_PALETTE (G9).

Usage : python -m design.vehicules  ->  app/assets/vehicules/{voiture,moto,velo,pieton,camion}.svg
"""

from __future__ import annotations

import math
from pathlib import Path

from design.tokens import VEHICULE_PALETTE as P

COS = math.cos(math.radians(30))
SIN = math.sin(math.radians(30))
S = 12                      # échelle monde -> pixels
OX, OY = 130, 118           # origine écran (viewBox 260 x 170)
VIEWBOX = "0 0 260 170"


def _iso(x: float, y: float, z: float) -> tuple[float, float]:
    return (OX + (x - y) * S * COS, OY + (x + y) * S * SIN - z * S)


def _poly(points: list[tuple[float, float]], fill: str, extra: str = "") -> str:
    pts = " ".join(f"{sx:.1f},{sy:.1f}" for sx, sy in points)
    return f'<polygon points="{pts}" fill="{fill}" {extra}/>'


def _box(x0, y0, z0, dx, dy, dz, haut, cote, face) -> str:
    """Un pavé isométrique : 3 faces visibles (dessus, côté +x, face +y)."""
    def p(x, y, z):
        return _iso(x0 + x, y0 + y, z0 + z)
    dessus = [p(0, 0, dz), p(dx, 0, dz), p(dx, dy, dz), p(0, dy, dz)]
    cote_x = [p(dx, 0, 0), p(dx, dy, 0), p(dx, dy, dz), p(dx, 0, dz)]      # face +x (éclairée)
    face_y = [p(0, dy, 0), p(dx, dy, 0), p(dx, dy, dz), p(0, dy, dz)]      # face +y (ombrée)
    return _poly(face_y, face) + _poly(cote_x, cote) + _poly(dessus, haut)


def _roue(cx: float, cy: float, r: float = 7) -> str:
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{r}" ry="{r * 0.7:.1f}" fill="{P["roue"]}"/>'
            f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{r * 0.42:.1f}" ry="{r * 0.3:.1f}" '
            f'fill="{P["jante"]}"/>')


def _ombre(cx: float, cy: float, rx: float, ry: float = None) -> str:
    ry = ry if ry is not None else rx * 0.32
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{P["sol"]}" opacity="0.14"/>')


def _svg(corps: str, label: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VIEWBOX}" role="img" '
            f'aria-label="Illustration : {label}">{corps}</svg>')


def voiture() -> str:
    h, c, f = P["corps-haut"], P["corps-cote"], P["corps-face"]
    th, tc, tf = P["toit-haut"], P["toit-cote"], P["toit-face"]
    roues = (_roue(*_iso(1.5, 4.3, 0)) + _roue(*_iso(6.6, 4.3, 0))
             + _roue(*_iso(1.5, 0.3, 0), 6) + _roue(*_iso(6.6, 0.3, 0), 6))
    corps = _box(0, 0, 0.5, 8.2, 4, 1.5, h, c, f)
    # Cabine (greenhouse) posée et bien insérée dans la carrosserie
    cx0, cy0, cz0, cdx, cdy, cdz = 2.2, 0.35, 2.0, 3.8, 3.3, 1.25
    cabine = _box(cx0, cy0, cz0, cdx, cdy, cdz, th, tc, tf)
    # Vitres : insérées dans les faces visibles de la cabine (pas flottantes)
    vitre_cote = _poly([_iso(cx0 + cdx, cy0 + 0.35, cz0 + 0.25),
                        _iso(cx0 + cdx, cy0 + cdy - 0.1, cz0 + 0.25),
                        _iso(cx0 + cdx, cy0 + cdy - 0.1, cz0 + cdz - 0.2),
                        _iso(cx0 + cdx, cy0 + 0.35, cz0 + cdz - 0.2)], P["verre"])
    vitre_face = _poly([_iso(cx0 + 0.3, cy0 + cdy, cz0 + 0.25),
                        _iso(cx0 + cdx - 0.2, cy0 + cdy, cz0 + 0.25),
                        _iso(cx0 + cdx - 0.2, cy0 + cdy, cz0 + cdz - 0.2),
                        _iso(cx0 + 0.3, cy0 + cdy, cz0 + cdz - 0.2)], P["verre-ombre"])
    # Montant central (séparation des vitres de la face +y)
    montant = _poly([_iso(cx0 + 1.9, cy0 + cdy, cz0 + 0.25),
                     _iso(cx0 + 2.1, cy0 + cdy, cz0 + 0.25),
                     _iso(cx0 + 2.1, cy0 + cdy, cz0 + cdz - 0.2),
                     _iso(cx0 + 1.9, cy0 + cdy, cz0 + cdz - 0.2)], tf)
    phare = _poly([_iso(8.2, 0.5, 1.0), _iso(8.2, 1.5, 1.0),
                   _iso(8.2, 1.5, 1.6), _iso(8.2, 0.5, 1.6)], P["phare"])
    feu = _poly([_iso(0, 2.6, 1.0), _iso(0, 3.7, 1.0),
                 _iso(0, 3.7, 1.6), _iso(0, 2.6, 1.6)], P["feu"])
    return _svg(_ombre(130, 150, 70) + roues + corps + cabine
                + vitre_face + montant + vitre_cote + phare + feu, "voiture")


def camion() -> str:
    h, c, f = P["corps-haut"], P["corps-cote"], P["corps-face"]
    ah, ac, af = P["alt-haut"], P["alt-cote"], P["alt-face"]
    roues = (_roue(*_iso(1.2, 4.4, 0)) + _roue(*_iso(4.6, 4.4, 0)) + _roue(*_iso(7.4, 4.4, 0))
             + _roue(*_iso(1.2, 0.2, 0), 6) + _roue(*_iso(4.6, 0.2, 0), 6)
             + _roue(*_iso(7.4, 0.2, 0), 6))
    remorque = _box(0, 0, 0.6, 5.6, 4, 3.4, ah, ac, af)
    cabine = _box(5.6, 0, 0.6, 2.8, 4, 2.4, h, c, f)
    pb = _poly([_iso(8.4, 0.4, 1.4), _iso(8.4, 3.6, 1.4),
                _iso(8.4, 3.6, 2.7), _iso(8.4, 0.4, 2.7)], P["verre"])
    phare = _poly([_iso(8.4, 0.3, 0.8), _iso(8.4, 1.2, 0.8),
                   _iso(8.4, 1.2, 1.2), _iso(8.4, 0.3, 1.2)], P["phare"])
    return _svg(_ombre(132, 150, 78) + roues + remorque + cabine + pb + phare, "poids lourd")


def _roue_rayons(cx, cy, r, couleur) -> str:
    rayons = "".join(
        f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx + r * math.cos(a):.1f}" '
        f'y2="{cy + r * 0.62 * math.sin(a):.1f}" stroke="{P["jante"]}" stroke-width="1"/>'
        for a in [math.radians(d) for d in range(0, 360, 45)])
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{r}" ry="{r * 0.62:.1f}" fill="none" '
            f'stroke="{couleur}" stroke-width="2.4"/>{rayons}')


def velo() -> str:
    # Vélo de profil, légèrement relevé, avec ombre portée pour la profondeur
    cadre = P["alt2-cote"]
    rx = 26
    r1x, r1y = 72, 128
    r2x, r2y = 188, 128
    roues = _roue_rayons(r1x, r1y, rx, P["roue"]) + _roue_rayons(r2x, r2y, rx, P["roue"])
    cadre_l = (f'<path d="M{r1x},{r1y} L130,86 L{r2x},{r2y} M130,86 L120,128 '
               f'M130,86 L150,72 L162,72 M120,128 L108,128 M150,72 L{r2x - 4},{r2y}" '
               f'fill="none" stroke="{cadre}" stroke-width="4.5" stroke-linejoin="round" '
               f'stroke-linecap="round"/>')
    selle = f'<rect x="100" y="66" width="22" height="6" rx="3" fill="{P["roue"]}"/>'
    guidon = f'<rect x="150" y="60" width="18" height="5" rx="2.5" fill="{P["roue"]}"/>'
    return _svg(_ombre(130, 150, 95, 10) + roues + cadre_l + selle + guidon, "vélo")


def moto() -> str:
    h, c, f = P["corps-haut"], P["corps-cote"], P["corps-face"]
    rx = 28
    r1x, r1y = 70, 126
    r2x, r2y = 190, 126
    roues = (f'<ellipse cx="{r1x}" cy="{r1y}" rx="{rx}" ry="{rx * 0.64:.1f}" fill="{P["roue"]}"/>'
             f'<ellipse cx="{r1x}" cy="{r1y}" rx="{rx * 0.4:.1f}" ry="{rx * 0.26:.1f}" '
             f'fill="{P["jante"]}"/>'
             f'<ellipse cx="{r2x}" cy="{r2y}" rx="{rx}" ry="{rx * 0.64:.1f}" fill="{P["roue"]}"/>'
             f'<ellipse cx="{r2x}" cy="{r2y}" rx="{rx * 0.4:.1f}" ry="{rx * 0.26:.1f}" '
             f'fill="{P["jante"]}"/>')
    corps = (f'<path d="M{r1x},110 Q110,84 150,92 L176,96 Q196,100 {r2x},112 L160,116 '
             f'Q120,120 96,118 Z" fill="{c}" stroke="{f}" stroke-width="1"/>')
    reservoir = f'<path d="M120,92 Q140,80 160,90 L150,100 Q134,104 122,100 Z" fill="{h}"/>'
    guidon = (f'<path d="M168,96 L188,74 L196,76" fill="none" stroke="{P["roue"]}" '
              f'stroke-width="4" stroke-linecap="round"/>')
    phare = f'<ellipse cx="196" cy="100" rx="6" ry="8" fill="{P["phare"]}"/>'
    return _svg(_ombre(130, 150, 92, 11) + roues + corps + reservoir + guidon + phare, "deux-roues")


def pieton() -> str:
    corps = P["alt-cote"]
    tete = f'<circle cx="130" cy="52" r="13" fill="{P["corps-cote"]}"/>'
    tronc = (f'<path d="M130,66 Q118,70 116,98 L120,126 L128,126 L130,100 L132,126 L140,126 '
             f'L144,98 Q142,70 130,66 Z" fill="{corps}"/>')
    bras = (f'<path d="M120,74 L106,98 M140,74 L154,96" fill="none" stroke="{corps}" '
            f'stroke-width="7" stroke-linecap="round"/>')
    return _svg(_ombre(130, 150, 34, 11) + bras + tronc + tete, "piéton")


VEHICULES = {"voiture": voiture, "moto": moto, "velo": velo, "pieton": pieton, "camion": camion}


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "app" / "assets" / "vehicules"
    out.mkdir(parents=True, exist_ok=True)
    for nom, fonction in VEHICULES.items():
        (out / f"{nom}.svg").write_text(fonction(), encoding="utf-8")


if __name__ == "__main__":
    main()
