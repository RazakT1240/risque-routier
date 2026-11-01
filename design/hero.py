"""Génère l'illustration du héros : route de campagne la nuit, sous la pluie (DESIGN §6.3).

Image générée (aucun droit tiers), couleurs lues dans tokens.HERO_PALETTE.
Sans accident ni personne. Cinémagraphe discret : la pluie tombe en boucle de 4 s,
uniquement si l'utilisateur n'a pas demandé de mouvement réduit.

Usage : python -m design.hero  ->  app/assets/hero-route-nuit.svg
"""

from __future__ import annotations

import random
from pathlib import Path

from design.tokens import HERO_PALETTE as P

W, H = 1600, 900
HORIZON = 500
VX = 860               # point de fuite


def _route() -> str:
    gauche_bas, droite_bas = -260, W + 120
    return (f'<polygon points="{VX - 8},{HORIZON} {VX + 8},{HORIZON} {droite_bas},{H} '
            f'{gauche_bas},{H}" fill="url(#chaussee)"/>')


def _ligne_bord(x_bas: float, largeur: float, opacite: float) -> str:
    return (f'<polygon points="{VX - 1},{HORIZON} {VX + 1},{HORIZON} {x_bas + largeur},{H} '
            f'{x_bas},{H}" fill="{P["marquage"]}" opacity="{opacite}"/>')


def _tirets() -> str:
    out = []
    t = 0.04
    while t < 1:
        t2 = min(t + 0.06 * (0.4 + t), 1)
        y1, y2 = HORIZON + (H - HORIZON) * t ** 1.6, HORIZON + (H - HORIZON) * t2 ** 1.6
        x = VX
        demi1, demi2 = 1 + 9 * t ** 1.6, 1 + 9 * t2 ** 1.6
        dx1 = (W * 0.5 - VX) * t ** 1.6
        dx2 = (W * 0.5 - VX) * t2 ** 1.6
        out.append(f'<polygon points="{x + dx1 - demi1},{y1:.1f} {x + dx1 + demi1},{y1:.1f} '
                   f'{x + dx2 + demi2},{y2:.1f} {x + dx2 - demi2},{y2:.1f}" '
                   f'fill="{P["marquage"]}" opacity="0.55"/>')
        t = t2 + 0.07 * (0.3 + t)
    return "".join(out)


def _reflets(rng: random.Random) -> str:
    """Traînées verticales des phares et feux sur la chaussée mouillée."""
    out = []
    for x, couleur, op in ((VX - 22, P["phare"], 0.35), (VX - 6, P["phare"], 0.3),
                           (VX + 40, P["feu-arriere"], 0.28), (VX + 52, P["feu-arriere"], 0.24)):
        largeur = 3
        for _ in range(26):
            y = rng.uniform(HORIZON + 6, H)
            t = (y - HORIZON) / (H - HORIZON)
            xx = VX + (x - VX) * (1 + 6 * t) + rng.uniform(-4, 4) * t
            hauteur = 4 + 40 * t
            opacite = op * (1 - t * 0.6)
            out.append(f'<rect x="{xx:.1f}" y="{y:.1f}" width="{largeur + 6 * t:.1f}" '
                       f'height="{hauteur:.1f}" fill="{couleur}" opacity="{opacite:.2f}" rx="2"/>')
    return "".join(out)


def _feux() -> str:
    def lumiere(cx, cy, r, couleur, halo):
        return (f'<circle cx="{cx}" cy="{cy}" r="{halo}" fill="url(#halo-{couleur[1:]})"/>'
                f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{couleur}"/>')
    return (lumiere(VX - 22, HORIZON + 6, 2.2, P["phare"], 46)
            + lumiere(VX - 6, HORIZON + 6, 2.2, P["phare"], 46)
            + lumiere(VX + 40, HORIZON + 12, 1.8, P["feu-arriere"], 22)
            + lumiere(VX + 52, HORIZON + 12, 1.8, P["feu-arriere"], 22))


def _relief() -> str:
    pts = [(0, HORIZON - 10), (180, HORIZON - 48), (360, HORIZON - 30), (520, HORIZON - 70),
           (700, HORIZON - 38), (VX, HORIZON - 14), (1040, HORIZON - 52), (1220, HORIZON - 28),
           (1400, HORIZON - 64), (W, HORIZON - 34), (W, HORIZON + 2), (0, HORIZON + 2)]
    return f'<polygon points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="{P["relief"]}"/>'


def _pluie(rng: random.Random) -> str:
    gouttes = []
    for _ in range(260):
        x, y = rng.uniform(-100, W + 100), rng.uniform(-H, H)
        long_ = rng.uniform(18, 46)
        op = rng.uniform(0.08, 0.28)
        gouttes.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x - long_ * 0.18:.0f}" '
                       f'y2="{y + long_:.0f}" stroke="{P["pluie"]}" stroke-width="1" '
                       f'opacity="{op:.2f}"/>')
    bloc = "".join(gouttes)
    return (f'<g class="pluie">{bloc}</g>'
            f'<g class="pluie" transform="translate(0 {H})">{bloc}</g>')


def build_svg(seed: int = 7) -> str:
    rng = random.Random(seed)
    halos = "".join(
        f'<radialGradient id="halo-{c[1:]}"><stop offset="0" stop-color="{c}" stop-opacity=".55"/>'
        f'<stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'
        for c in (P["phare"], P["feu-arriere"]))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" \
preserveAspectRatio="xMidYMid slice" role="img" \
aria-label="Route de campagne la nuit sous la pluie">
<defs>
<linearGradient id="ciel" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="{P["ciel-haut"]}"/><stop offset="1" stop-color="{P["ciel-horizon"]}"/>
</linearGradient>
<radialGradient id="ville" cx="0.54" cy="1" r="0.5">
<stop offset="0" stop-color="{P["halo-ville"]}" stop-opacity=".9"/>
<stop offset="1" stop-color="{P["halo-ville"]}" stop-opacity="0"/></radialGradient>
<linearGradient id="chaussee" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="{P["chaussee-loin"]}"/><stop offset="1" stop-color="{P["chaussee"]}"/>
</linearGradient>
{halos}
<style>
@media (prefers-reduced-motion: no-preference) {{
  .pluie-anim {{ animation: tombe 4s linear infinite; }}
}}
@keyframes tombe {{ from {{ transform: translateY(0); }} to {{ transform: translateY({H}px); }} }}
</style>
</defs>
<rect width="{W}" height="{HORIZON + 4}" fill="url(#ciel)"/>
<rect y="{HORIZON - 260}" width="{W}" height="264" fill="url(#ville)"/>
{_relief()}
<rect y="{HORIZON}" width="{W}" height="{H - HORIZON}" fill="{P["relief"]}"/>
{_route()}
{_ligne_bord(-210, 26, 0.35)}
{_ligne_bord(W + 40, 26, 0.35)}
{_tirets()}
{_reflets(rng)}
{_feux()}
<g class="pluie-anim">{_pluie(rng)}</g>
</svg>"""


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "app" / "assets" / "hero-route-nuit.svg"
    out.write_text(build_svg(), encoding="utf-8")


if __name__ == "__main__":
    main()
