"""Templates Plotly « route_clair » / « route_sombre » générés depuis les tokens (§8)."""

import plotly.graph_objects as go
import plotly.io as pio

from design.tokens import FONT_SANS, TRANSPARENT, tokens


def make_template(t: dict) -> go.layout.Template:
    return go.layout.Template(layout=dict(
        font=dict(family=FONT_SANS, size=13, color=t["text-secondary"]),
        paper_bgcolor=TRANSPARENT, plot_bgcolor=TRANSPARENT,
        colorway=[t["data-neutre"], t["data-neutre-clair"]],
        margin=dict(l=8, r=8, t=8, b=8),
        separators=",\u00a0",            # virgule décimale, espace insécable milliers
        xaxis=dict(showgrid=False, zeroline=False, showline=True, linecolor=t["border"],
                   ticks="outside", tickcolor=t["border"], tickfont=dict(size=12),
                   automargin=True),
        yaxis=dict(showgrid=True, gridcolor=t["border"], gridwidth=1, zeroline=False,
                   showline=False, tickfont=dict(size=12), automargin=True),
        hoverlabel=dict(bgcolor=t["bg-surface"], bordercolor=t["border"],
                        font=dict(family=FONT_SANS, size=13, color=t["text-primary"])),
        legend=dict(orientation="h", y=-0.18, font=dict(size=12)),
        title=dict(text=""),                  # le titre vit dans la carte, pas dans la figure
    ))


TEMPLATES = {"light": make_template(tokens("light")), "dark": make_template(tokens("dark"))}
pio.templates["route_clair"] = TEMPLATES["light"]
pio.templates["route_sombre"] = TEMPLATES["dark"]


def template_name(scheme: str) -> str:
    return "route_sombre" if scheme == "dark" else "route_clair"
