"""QA : chaque page × combinaisons de filtres -> erreurs de callback, erreurs console, durées.

Usage : python sandbox/qa_filtres.py [url_base]
"""

import sys
import time

from playwright.sync_api import sync_playwright

PAGES = ["/", "/vue-ensemble", "/paradoxe", "/qui", "/ou-quand", "/evolution", "/simulateur",
         "/methode"]
FILTRES = ["", "?annee=cumul&dep=29", "?annee=2020&dep=48", "?annee=2019&dep=75",
           "?annee=2023&dep=2A"]


def main(base: str) -> int:
    problemes = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.on("pageerror", lambda e: problemes.append(f"pageerror {pg.url}: {e}"))
        pg.on("console", lambda m: problemes.append(f"console {pg.url}: {m.text}")
              if m.type == "error" else None)
        pg.on("response", lambda r: problemes.append(f"HTTP {r.status} {pg.url}")
              if "_dash-update-component" in r.url and r.status >= 400 else None)
        for page in PAGES:
            for f in FILTRES:
                t0 = time.perf_counter()
                pg.goto(base + page + f, wait_until="networkidle")
                duree = time.perf_counter() - t0
                print(f"{page + f:<36} {duree:5.2f} s")
        # Changement de filtre : durée jusqu'au retour au repos réseau
        pg.goto(base + "/vue-ensemble", wait_until="networkidle")
        t0 = time.perf_counter()
        pg.goto(base + "/vue-ensemble?annee=2022&dep=13", wait_until="networkidle")
        print(f"changement de filtre (rechargement complet) : {time.perf_counter() - t0:.2f} s")
        b.close()
    print("\n".join(problemes) or "aucun problème")
    return len(problemes)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8050"))
