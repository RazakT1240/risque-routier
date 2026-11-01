"""Captures QA (playwright, outil de vérification uniquement) : clair / sombre, 1440 / 390 px.

Usage : python sandbox/qa_screens.py <url_base> <dossier_sortie> <[nom=]chemin> [...]
Relève aussi les erreurs de la console navigateur dans <dossier_sortie>/console.txt.
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

LARGEURS = {"1440": (1440, 900), "1024": (1024, 768), "390": (390, 844)}
SCHEMES = ("light", "dark")


def slug(path: str) -> tuple[str, str]:
    """'nom=/chemin' -> (nom, chemin) ; '/chemin' -> nom dérivé du chemin."""
    if "=" in path:
        nom, chemin = path.split("=", 1)
        return nom, chemin
    return path.strip("/").replace("/", "_") or "accueil", path


def main(base: str, out: str, paths: list[str]) -> None:
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)
    erreurs: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for scheme in SCHEMES:
            for nom, (w, h) in LARGEURS.items():
                ctx = browser.new_context(viewport={"width": w, "height": h},
                                          reduced_motion="reduce")
                # Mantine lit ce choix au chargement
                ctx.add_init_script(
                    f"localStorage.setItem('mantine-color-scheme-value', '{scheme}');")
                page = ctx.new_page()
                page.on("console", lambda m, s=scheme, n=nom: erreurs.append(
                    f"[{s} {n}] {m.type}: {m.text}") if m.type in ("error", "warning") else None)
                page.on("pageerror", lambda e, s=scheme, n=nom: erreurs.append(
                    f"[{s} {n}] pageerror: {e}"))
                for item in paths:
                    nom_page, path = slug(item)
                    page.goto(base.rstrip("/") + path, wait_until="networkidle")
                    page.wait_for_timeout(1500)
                    page.screenshot(path=str(out_dir / f"{nom_page}_{scheme}_{nom}.png"),
                                    full_page=True)
                ctx.close()
        browser.close()
    (out_dir / "console.txt").write_text("\n".join(erreurs) or "aucune erreur", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
