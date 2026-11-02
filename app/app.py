"""Application « Risque routier » — Dash + Dash Mantine Components.

Lancer : python app/app.py  ->  http://127.0.0.1:8050
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlencode

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import dash  # noqa: E402
import dash_mantine_components as dmc  # noqa: E402
from dash import Dash, Input, Output, State, ctx, dcc, no_update  # noqa: E402

import design.plotly_template  # noqa: E402,F401  (enregistre les templates)
from app import auth, callbacks_globaux  # noqa: E402
from app import data_access as da  # noqa: E402
from app.components import assistant_ui, shell  # noqa: E402
from app.scenes import PAR_CHEMIN, SCENES  # noqa: E402
from design.theme import THEME  # noqa: E402
from design.tokens import FONTS_URL  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")

app = Dash(__name__, use_pages=True, pages_folder=str(HERE / "pages"),
           assets_folder=str(HERE / "assets"), external_stylesheets=[FONTS_URL],
           title="Risque routier · fréquence, gravité, coût",
           update_title=None, suppress_callback_exceptions=True)
server = app.server
auth.register(server)  # garde d'accès : connexion avant le tableau de bord
# Langue du document (lecteurs d'écran, G12)
app.index_string = app.index_string.replace("<html>", '<html lang="fr">', 1)

ANNEES_VALIDES = {str(a) for a in da.annees(da.PERIODE_CUMUL)} | {da.PERIODE_CUMUL}
DEPS_VALIDES = {d["dep"] for d in da.departements_metropole()} | {da.TERRITOIRE_FRANCE}

app.layout = dmc.MantineProvider(theme=THEME, defaultColorScheme="light", children=[
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="filtres", storage_type="session"),
    *callbacks_globaux.stores(),
    shell.app_shell(dash.page_container, da.annees(da.PERIODE_CUMUL),
                    da.departements_metropole(), da.DERNIERE_ANNEE),
    callbacks_globaux.modales(),
    assistant_ui.widget(),
])
callbacks_globaux.register(app)
shell.register(app)
assistant_ui.register(app)


@app.callback(
    Output("filtre-periode", "value"), Output("filtre-territoire", "value"),
    Output("url", "search"), Output("filtres", "data"),
    Input("url", "search"), Input("filtre-periode", "value"),
    Input("filtre-territoire", "value"), State("filtres", "data"))
def synchroniser_filtres(search, periode, territoire, memo):
    """URL <-> sélecteurs <-> session. Une URL sans paramètre (navigation) garde les filtres."""
    if ctx.triggered_id == "url" or ctx.triggered_id is None:
        params = parse_qs((search or "").lstrip("?"))
        p = params.get("annee", [None])[0]
        d = params.get("dep", [None])[0]
        if p is None and d is None and memo:
            p, d = memo.get("periode"), memo.get("dep")
        periode = p if p in ANNEES_VALIDES else (periode or str(da.DERNIERE_ANNEE))
        territoire = d if d in DEPS_VALIDES else (territoire or da.TERRITOIRE_FRANCE)
    query = {"annee": periode}
    if territoire != da.TERRITOIRE_FRANCE:
        query["dep"] = territoire
    nouvelle = "?" + urlencode(query)
    return (periode, territoire, nouvelle if nouvelle != search else no_update,
            {"periode": periode, "dep": territoire})


@app.callback(Output("progress-rule", "style"), Output("scene-compteur", "children"),
              Input("_pages_location", "pathname"))
def progression(path):
    scene = PAR_CHEMIN.get(path or "/", SCENES[0])
    return ({"width": f"{scene['num'] / len(SCENES) * 100:.1f}%"},
            f"Scène {scene['num']} / {len(SCENES)} · {scene['nom']}")


if __name__ == "__main__":
    app.run(debug=os.getenv("DASH_DEBUG", "1") == "1", port=8050,
            dev_tools_ui=os.getenv("DASH_QA") != "1", dev_tools_disable_version_check=True)
