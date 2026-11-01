"""Thème MantineProvider généré depuis les tokens (DESIGN_SYSTEM.md §5).

Clés vérifiées contre la doc de DMC 2.8 / Mantine 8 (theme object).
"""

from design.tokens import AMBRE, ARDOISE, FONT_MONO, FONT_SANS, FONT_SERIF, GRAVITE, RADIUS

THEME = {
    "primaryColor": "ambre",
    "primaryShade": {"light": 6, "dark": 5},
    "colors": {"ambre": AMBRE, "gravite": GRAVITE, "ardoise": ARDOISE},
    "fontFamily": FONT_SANS,
    "fontFamilyMonospace": FONT_MONO,
    "headings": {"fontFamily": FONT_SERIF, "fontWeight": "500"},
    "defaultRadius": "md",
    "radius": {k: f"{v}px" for k, v in RADIUS.items()},
    "components": {
        "Button": {"defaultProps": {"radius": "sm", "fw": 500}},
        "Paper": {"defaultProps": {"radius": "md", "withBorder": True, "p": "lg"}},
        "NavLink": {"defaultProps": {"variant": "light"}},
        "SegmentedControl": {"defaultProps": {"radius": "sm"}},
    },
}
