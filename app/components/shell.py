"""Coquille de l'application : header (§6.1), filtres globaux (BRIEF §4), navbar (§6.7)."""

from __future__ import annotations

import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

from app.scenes import SCENES

PERIODE_CUMUL = "cumul"
TERRITOIRE_FRANCE = "FR"


def filtre(label: str, icon: str, composant) -> html.Div:
    return html.Div(children=[
        html.Div(className="filtre-label", children=[
            DashIconify(icon=icon, width=12, className="t-secondary"),
            html.Span(label, className="label", style={"fontSize": 11, "lineHeight": "14px"})]),
        composant])


def filtres(annees: list[int], departements: list[dict], annee_defaut: int) -> dmc.Popover:
    """Bouton-résumé des filtres (période · territoire) qui ouvre un panneau :
    années en sélecteur segmenté, recherche de département, raccourcis, réinitialisation.
    Le panneau reste monté (keepMounted) : les callbacks lisent toujours les deux contrôles."""
    periode = dmc.SegmentedControl(
        id="filtre-periode", value=str(annee_defaut), fullWidth=True, size="xs",
        data=[{"value": PERIODE_CUMUL, "label": f"{annees[0]}–{annees[-1]}"}]
        + [{"value": str(a), "label": str(a)} for a in annees],
        **{"aria-label": "Période"})
    territoire = dmc.Select(
        id="filtre-territoire", searchable=True, allowDeselect=False, value=TERRITOIRE_FRANCE,
        nothingFoundMessage="Aucun département", placeholder="Rechercher un département…",
        comboboxProps={"withinPortal": False}, maxDropdownHeight=260,
        leftSection=DashIconify(icon="tabler:search", width=16),
        data=[{"value": TERRITOIRE_FRANCE, "label": "France métropolitaine"}]
        + [{"value": d["dep"], "label": f"{d['dep']} · {d['nom']}"} for d in departements],
        **{"aria-label": "Territoire"})
    panneau = html.Div(className="panneau-filtres", children=[
        html.Div(className="panneau-section", children=[
            html.Div(className="panneau-titre", children=[
                DashIconify(icon="tabler:calendar", width=14), html.Span("Période")]),
            periode,
            html.Div("Les courbes d'évolution montrent toujours les 7 années.",
                     className="caption", style={"marginTop": 6}),
        ]),
        html.Div(className="panneau-section", children=[
            html.Div(className="panneau-titre", children=[
                DashIconify(icon="tabler:map-2", width=14), html.Span("Territoire")]),
            territoire,
            dmc.Group(gap=6, mt=8, children=[
                html.Button("France métropolitaine", id="filtre-france", n_clicks=0,
                            className="chip-raccourci"),
                html.Button("Département le plus touché", id="filtre-pire", n_clicks=0,
                            className="chip-raccourci"),
            ]),
        ]),
        html.Div(className="panneau-pied", children=[
            html.Button([DashIconify(icon="tabler:refresh", width=14),
                         html.Span("Réinitialiser")], id="filtre-reset", n_clicks=0,
                        className="btn btn-precedent btn-sm"),
            html.Span("Les filtres s'appliquent à toutes les scènes et à l'adresse de la page.",
                      className="caption"),
        ]),
    ])
    return dmc.Popover(
        id="popover-filtres", position="bottom-end", width=440, shadow="md", radius="md",
        keepMounted=True, withArrow=False, offset=8, trapFocus=False, zIndex=300,
        children=[
            dmc.PopoverTarget(html.Button(
                id="filtres-resume", className="filtres-resume", n_clicks=0,
                **{"aria-label": "Ouvrir les filtres"},
                children=[
                    DashIconify(icon="tabler:adjustments-horizontal", width=16,
                                className="t-accent"),
                    html.Span(id="resume-periode", className="resume-valeur",
                              children=str(annee_defaut)),
                    html.Span("·", className="resume-sep"),
                    html.Span(id="resume-territoire", className="resume-valeur resume-terr",
                              children="France métropolitaine"),
                    DashIconify(icon="tabler:chevron-down", width=14, className="t-muted"),
                ])),
            dmc.PopoverDropdown(panneau),
        ])


def header(annees, departements, annee_defaut) -> dmc.AppShellHeader:
    return dmc.AppShellHeader(className="app-header", children=[
        html.Div(className="header-inner", children=[
            dmc.Group(gap=12, wrap="nowrap", children=[
                dmc.Burger(id="burger", size="sm", hiddenFrom="sm",
                           **{"aria-label": "Ouvrir la navigation"}),
                html.Div("R", className="monogramme", **{"aria-hidden": "true"}),
                html.Div(className="brand-text", children=[
                    html.Div("Risque routier", className="brand-title"),
                    html.Div("Fréquence · Gravité · Coût", className="label",
                             style={"fontSize": 10, "lineHeight": "12px"}),
                ]),
            ]),
            html.Div(id="scene-compteur", className="caption header-centre"),
            dmc.Group(gap=16, wrap="nowrap", children=[
                html.Div(filtres(annees, departements, annee_defaut), className="header-filtres"),
                dmc.ColorSchemeToggle(
                    id="theme-toggle", variant="default", size="lg",
                    lightIcon=DashIconify(icon="tabler:moon", width=18),
                    darkIcon=DashIconify(icon="tabler:sun", width=18),
                    **{"aria-label": "Basculer le thème clair / sombre"}),
                html.A(DashIconify(icon="tabler:logout", width=18), href="/logout",
                       className="header-logout", title="Se déconnecter",
                       **{"aria-label": "Se déconnecter"}),
            ]),
        ]),
        html.Div(className="progress-track", children=html.Div(
            id="progress-rule", className="progress-rule", style={"width": "0%"})),
    ])


def navbar() -> dmc.AppShellNavbar:
    return dmc.AppShellNavbar(className="app-navbar", p="md", children=dmc.Stack(
        gap=4, h="100%", children=[
        html.Div("Challenge Dataviz · Institut des Actuaires", className="nav-badge"),
        html.Div(style={"height": 12}),
        *[dmc.NavLink(
            href=s["path"], active="exact", className="nav-link",
            **{"aria-label": f"Scène {s['num']} : {s['nom']}"},
            label=html.Span(s["nom"]),
            leftSection=dmc.Group(gap=8, wrap="nowrap", children=[
                html.Span(f"{s['num']:02d}", className="nav-num"),
                DashIconify(icon=s["icon"], width=18)]),
        ) for s in SCENES],
        html.Div(style={"flex": 1}),
        html.Button(id="nav-replier", className="nav-replier", n_clicks=0, title="Replier le menu",
                    **{"aria-label": "Replier ou déplier le menu", "aria-expanded": "true"},
                    children=[DashIconify(icon="tabler:layout-sidebar-left-collapse", width=18,
                                          className="ico-replier"),
                              DashIconify(icon="tabler:layout-sidebar-left-expand", width=18,
                                          className="ico-deplier"),
                              html.Span("Replier le menu", className="nav-replier-texte")]),
    ]))


def app_shell(contenu, annees, departements, annee_defaut) -> dmc.AppShell:
    """AppShell : navbar 240 px dès 1200 px, icônes seules (72 px) de 768 à 1199 px,
    burger sous 768 px (DESIGN §10)."""
    return dmc.AppShell(
        id="appshell", padding=0,
        header={"height": 64},
        navbar={"width": 240, "breakpoint": 768, "collapsed": {"mobile": True}},
        children=[header(annees, departements, annee_defaut), navbar(),
                  dmc.AppShellMain(contenu)])


def register(app) -> None:
    from dash import Input, Output, State, ctx, no_update

    from app import data_access as da

    @app.callback(Output("resume-periode", "children"), Output("resume-territoire", "children"),
                  Input("filtre-periode", "value"), Input("filtre-territoire", "value"))
    def resume_filtres(periode, dep):
        return (da.libelle_periode(periode),
                "France métropolitaine" if dep in (None, TERRITOIRE_FRANCE)
                else da.libelle_territoire(dep))

    @app.callback(Output("filtre-territoire", "value", allow_duplicate=True),
                  Output("filtre-periode", "value", allow_duplicate=True),
                  Input("filtre-france", "n_clicks"), Input("filtre-pire", "n_clicks"),
                  Input("filtre-reset", "n_clicks"), prevent_initial_call=True)
    def raccourcis(_france, _pire, _reset):
        if ctx.triggered_id == "filtre-france":
            return TERRITOIRE_FRANCE, no_update
        if ctx.triggered_id == "filtre-pire":
            t = da.table("ind_territoires")
            t = t[t["periode"] == da.LIBELLE_PERIODE_CUMUL].dropna(subset=["taux_tues_million"])
            return t.loc[t["taux_tues_million"].idxmax(), "dep"], no_update
        return TERRITOIRE_FRANCE, str(da.DERNIERE_ANNEE)

    @app.callback(Output("appshell", "navbar"), Input("burger", "opened"),
                  State("appshell", "navbar"))
    def basculer_navbar(ouvert, nav):
        nav["collapsed"] = {"mobile": not ouvert}
        return nav

    @app.callback(Output("burger", "opened"), Input("_pages_location", "pathname"),
                  prevent_initial_call=True)
    def fermer_burger(_):
        """Après un choix de scène sur mobile, la navigation se referme."""
        return False
