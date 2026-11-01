"""Thème MantineProvider généré depuis les tokens (DESIGN_SYSTEM.md §5).

Clés vérifiées contre la doc de DMC 2.8 / Mantine 8 (theme object).
"""

from design.tokens import (
    AMBRE,
    ARDOISE,
    FONT_MONO,
    FONT_SANS,
    FONT_SERIF,
    GRAVITE,
    MANTINE_DARK,
    MANTINE_GRAY,
    RADIUS,
)

THEME = {
    "primaryColor": "ambre",
    "primaryShade": {"light": 6, "dark": 5},
    # Texte foncé sur l'ambre plein (contraste AA) : Mantine choisit noir/blanc selon la luminance
    "autoContrast": True,
    "colors": {"ambre": AMBRE, "gravite": GRAVITE, "ardoise": ARDOISE, "dark": MANTINE_DARK,
               "gray": MANTINE_GRAY},
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
