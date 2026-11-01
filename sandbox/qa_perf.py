"""QA performances : premier affichage de chaque scène et durée des callbacks lors d'un
changement de filtre fait dans l'interface (sélecteur Territoire).

Usage : python sandbox/qa_perf.py [url_base]
"""

import sys
import time

from playwright.sync_api import sync_playwright

PAGES = ["/", "/vue-ensemble", "/paradoxe", "/qui", "/ou-quand", "/evolution", "/simulateur",
         "/methode"]


def main(base: str) -> None:
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        durees: list[tuple[str, float]] = []

        def sur_reponse(r):
            if "_dash-update-component" in r.url:
                t = r.request.timing
                durees.append((r.request.post_data_json.get("output", "?")[:60],
                               t["responseEnd"] - t["requestStart"]))

        pg.on("response", sur_reponse)
        print("Premier affichage (navigation jusqu'au repos réseau)")
        for page in PAGES:
            t0 = time.perf_counter()
            pg.goto(base + page, wait_until="networkidle")
            print(f"  {page:<15} {time.perf_counter() - t0:5.2f} s")
        print("\nChangement de territoire dans l'interface (callbacks serveur, ms)")
        for page in ["/vue-ensemble", "/paradoxe", "/qui", "/ou-quand", "/evolution"]:
            pg.goto(base + page, wait_until="networkidle")
            pg.wait_for_timeout(500)
            durees.clear()
            t0 = time.perf_counter()
            champ = pg.locator("#filtre-territoire")
            champ.click()
            champ.fill("29")
            pg.keyboard.press("ArrowDown")
            pg.keyboard.press("Enter")
            pg.wait_for_timeout(2500)
            total = None
            valeur = pg.input_value("#filtre-territoire")
            pire = max(durees, key=lambda d: d[1]) if durees else ("-", 0)
            somme = sum(d for _, d in durees)
            print(f"  {page:<14} [{valeur}] {len(durees):2d} callbacks, le plus lent "
                  f"{pire[1]:6.0f} ms ({pire[0]}), somme {somme:5.0f} ms")
            _ = (t0, total)
        b.close()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8050")
