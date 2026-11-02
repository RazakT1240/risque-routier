"""Scène 07 — Simulateur : risque relatif de blessure grave d'un profil donné.

Calcul côté client (app/assets/simulateur.js) à partir de models/simulateur.json.
"""

from __future__ import annotations

import math

import dash
import dash_mantine_components as dmc
from dash import ClientsideFunction, Input, Output, State, clientside_callback, dcc, html
from dash_iconify import DashIconify

from app import data_access as da
from app import i18n
from app.components.blocks import insight, scene_header, scene_layout, scene_nav
from app.components.format import fmt_number, fmt_pct
from app.scenes import voisines


def _note_modele(m) -> list[str]:
    n = fmt_number(m["n_obs"])
    if i18n.langue() == "en":
        return [f"Statistical estimate over {da.PREMIERE_ANNEE}–{da.DERNIERE_ANNEE}, not an "
                "individual prediction. ",
                f"Model: logistic regression on {n} involved users (Metropolitan France); "
                "\"rain\" = light rain (0.2 to 5 mm) on the day in the department; reference: "
                "observed share of seriously injured among involved users."]
    return ["Estimation statistique sur 2019–2025, pas une prédiction individuelle. ",
            f"Modèle : régression logistique sur {n} usagers impliqués (France métropolitaine) ; "
            "« pluie » = pluie faible (0,2 à 5 mm) du jour dans le département ; référence : part "
            "observée de blessés graves parmi les usagers impliqués."]

dash.register_page(__name__, path="/simulateur", name="Simulateur", order=7,
                   title="Simulateur · Risque routier")
NUM = 7
GRADUATIONS = [1 / 8, 1 / 4, 1 / 2, 1, 2, 4, 8]


def _modele():
    return da.modele("simulateur")


def _or(var, niveau):
    c = _modele()["coefs"][var].get(niveau)
    return math.exp(c["coef"]) if c else None


def titre():
    m = _modele()
    types = {k: math.exp(v["coef"]) for k, v in m["coefs"]["type_usager"].items()}
    lieu = _or("agg_lib", "Hors agglomération") or 1
    contexte = max(_or("nuit", "Oui") or 1, _or("meteo_cat", "pluie faible") or 1)
    mode = max(max(types.values()), lieu) > contexte
    if i18n.langue() == "en":
        return (("The mode of travel and the place", "weigh more than night or rain.") if mode
                else ("Driving conditions", "weigh more than the user's profile."))
    return (("Le mode de déplacement et le lieu", "pèsent plus que la nuit ou la pluie.") if mode
            else ("Les conditions de circulation", "pèsent plus que le profil de l'usager."))


def chapeau():
    m = _modele()
    pct = fmt_pct(m["taux_observe"] * 100, 0)
    if i18n.langue() == "en":
        return (f"Among road users involved in an injury crash between {da.PREMIERE_ANNEE} and "
                f"{da.DERNIERE_ANNEE}, {pct} were killed or hospitalised. Build a profile to see "
                "how this risk changes.")
    return (f"Parmi les usagers impliqués dans un accident corporel entre {da.PREMIERE_ANNEE} et "
            f"{da.DERNIERE_ANNEE}, {pct} ont été tués ou hospitalisés. Composez un profil pour "
            "voir comment ce risque change.")


def et_alors():
    hors = fmt_number(_or("agg_lib", "Hors agglomération"), 1)
    nuit = fmt_number(_or("nuit", "Oui"), 1)
    if i18n.langue() == "en":
        return (f"All else equal, the odds of a serious injury are multiplied by {hors} outside "
                f"built-up areas and by {nuit} at night (model odds ratios): usage variables, "
                "observable via telematics, that complement classic pricing criteria.")
    return (f"À profil égal, la cote d'une blessure grave est multipliée par {hors} hors "
            f"agglomération et par {nuit} la nuit (rapports de cotes du modèle) : des variables "
            "d'usage, observables par la télématique, qui complètent les critères tarifaires "
            "classiques.")


def _jauge():
    lo, hi = math.log(GRADUATIONS[0]), math.log(GRADUATIONS[-1])
    ticks = [html.Span(f"÷{fmt_number(1 / g)}" if g < 1 else f"×{fmt_number(g)}",
                       className="jauge-tick",
                       style={"left": f"{(math.log(g) - lo) / (hi - lo) * 100:.1f}%"})
             for g in GRADUATIONS]
    un = f"{-lo / (hi - lo) * 100:.1f}%"
    return html.Div(className="jauge", children=[
        html.Div(className="jauge-piste", children=[
            html.Div(className="jauge-un", style={
                "left": f"{-lo / (hi - lo) * 100:.1f}%"}),
            html.Div(id="sim-marqueur", className="jauge-marqueur", style={"left": un}),
        ]),
        html.Div(className="jauge-ticks", children=ticks),
        html.Div(className="caption", style={"marginTop": 22},
                 children=i18n.t("sim.jauge_note")),
    ])


def controle(label, icon, composant):
    return html.Div(children=[
        html.Div(className="filtre-label", children=[DashIconify(icon=icon, width=14),
                                                     html.Span(label, className="label")]),
        composant])


def layout(**_):
    m = _modele()
    n = m["niveaux"]
    classes = n["classe_age"]
    debut, accent = titre()
    profil = html.Section(className="carte", children=dmc.Stack(gap=20, children=[
        html.H2(i18n.t("sim.profil"), className="h2"),
        controle(i18n.t("sim.type"), "tabler:user", dmc.SegmentedControl(
            id="sim-type", data=i18n.opt("type_usager", n["type_usager"]), value="2RM",
            orientation="vertical", fullWidth=True, **{"aria-label": i18n.t("sim.type")})),
        controle(i18n.t("sim.age"), "tabler:calendar-user", html.Div([
            html.Div(id="sim-age-lib", className="t-primary", style={"fontWeight": 600}),
            dmc.Slider(id="sim-age", min=0, max=len(classes) - 1, step=1,
                       value=classes.index("20-24"), label=None, mt=8, mb=24,
                       marks=[{"value": i, "label": c.split("-")[0]}
                              for i, c in enumerate(classes) if i % 4 == 0],
                       **{"aria-label": i18n.t("sim.age")}),
        ])),
        controle(i18n.t("sim.sexe"), "tabler:gender-bigender", dmc.SegmentedControl(
            id="sim-sexe", data=i18n.opt("sexe", n["sexe_lib"]), value="Homme", fullWidth=True,
            **{"aria-label": i18n.t("sim.sexe")})),
        dmc.Group(gap=24, children=[
            dmc.Switch(id="sim-nuit", label=i18n.t("sim.nuit"), checked=True),
            dmc.Switch(id="sim-pluie", label=i18n.t("sim.pluie"), checked=True),
            dmc.Switch(id="sim-hors", label=i18n.t("sim.hors"), checked=True),
        ]),
        controle(i18n.t("sim.route"), "tabler:road", dmc.Select(
            id="sim-route", data=i18n.opt("route", n["catr_groupe"]), value="Départementale",
            allowDeselect=False, comboboxProps={"withinPortal": True},
            **{"aria-label": i18n.t("sim.route")})),
    ]))
    scene = html.Div(className="sim-scene", children=[
        html.Div(className="sim-stage", children=html.Img(
            id="sim-vehicule", className="sim-vehicule", src="/assets/vehicules/moto.svg",
            alt=i18n.t("sim.vehicule_alt"))),
        html.Div(id="sim-badge", className="sim-badge sim-badge-neutre", children="—"),
    ])
    resultat = html.Section(className="carte carte-resultat", **{"aria-live": "polite"},
                            children=dmc.Stack(gap=20, children=[
            html.H2(i18n.t("sim.resultat"), className="h2"),
            scene,
            dmc.Group(gap=40, align="flex-end", children=[
                html.Div([html.Div(i18n.t("sim.risque_relatif"), className="label"),
                          html.Div(id="sim-ratio", className="display num t-primary")]),
                html.Div([html.Div(i18n.t("sim.proba"), className="label"),
                          html.Div(id="sim-proba", className="kpi-value")]),
            ]),
            _jauge(),
            html.P(id="sim-phrase", className="body t-primary recit", style={"margin": 0}),
            html.Div(dmc.Button(i18n.t("sim.comparer"), id="sim-comparer", n_clicks=0,
                                variant="light",
                                leftSection=DashIconify(icon="tabler:arrows-left-right",
                                                        width=16))),
            html.Div(id="sim-comparaison", style={"display": "none"}, children=[
                html.Div(className="comp-ligne", children=[
                    html.Span(i18n.t("sim.moyenne"), className="comp-lib"),
                    html.Div(className="comp-piste", children=html.Div(
                        id="sim-comp-moy", className="comp-barre comp-neutre")),
                    html.Span(id="sim-comp-moy-txt", className="comp-val")]),
                html.Div(className="comp-ligne", children=[
                    html.Span(i18n.t("sim.profil_choisi"), className="comp-lib"),
                    html.Div(className="comp-piste", children=html.Div(
                        id="sim-comp-profil", className="comp-barre comp-alerte")),
                    html.Span(id="sim-comp-profil-txt", className="comp-val")]),
            ]),
            html.Div(className="caption", children=_note_modele(m)),
        ]))
    return scene_layout(
        dcc.Store(id="sim-modele",
                  data={**m, "jauge": [GRADUATIONS[0], GRADUATIONS[-1]], "lang": i18n.langue()}),
        scene_header(NUM, i18n.nom_scene("/simulateur"), debut, accent, chapeau()),
        html.Div(className="grille-simu", children=[profil, resultat]),
        insight(et_alors()),
        scene_nav(*voisines(NUM)),
    )


clientside_callback(
    ClientsideFunction(namespace="simulateur", function_name="calcul"),
    Output("sim-ratio", "children"), Output("sim-proba", "children"),
    Output("sim-phrase", "children"), Output("sim-marqueur", "style"),
    Output("sim-marqueur", "className"), Output("sim-comparaison", "style"),
    Output("sim-comp-moy", "style"), Output("sim-comp-profil", "style"),
    Output("sim-comp-moy-txt", "children"), Output("sim-comp-profil-txt", "children"),
    Output("sim-badge", "children"), Output("sim-badge", "className"),
    Input("sim-type", "value"), Input("sim-age", "value"), Input("sim-sexe", "value"),
    Input("sim-nuit", "checked"), Input("sim-pluie", "checked"), Input("sim-hors", "checked"),
    Input("sim-route", "value"), Input("sim-comparer", "n_clicks"), State("sim-modele", "data"))

clientside_callback(
    ClientsideFunction(namespace="simulateur", function_name="vehicule"),
    Output("sim-vehicule", "src"), Output("sim-vehicule", "alt"),
    Input("sim-type", "value"), State("sim-modele", "data"))

clientside_callback(
    ClientsideFunction(namespace="simulateur", function_name="age"),
    Output("sim-age-lib", "children"), Input("sim-age", "value"), State("sim-modele", "data"))
