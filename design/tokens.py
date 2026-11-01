"""SOURCE UNIQUE des valeurs visuelles « Route de nuit » (DESIGN_SYSTEM.md §2-§4, G9).

Aucun hexadécimal ne doit apparaître ailleurs que dans ce fichier et app/assets/custom.css.
Indépendant de Dash (réutilisable pour la version Quarto).
"""

# --- Couleurs : interface + données, par mode (§2.1, §2.2) -----------------
LIGHT = {
    "bg-page": "#F6F4EF",
    "bg-surface": "#FFFFFF",
    "bg-subtle": "#EDEAE3",
    "border": "#DEDAD1",
    "text-primary": "#1B1F24",
    "text-secondary": "#5A6270",
    "text-muted": "#8A909A",
    "accent": "#E0A100",
    "accent-text": "#8A6100",
    "grav-tue": "#B3261E",
    "grav-hospi": "#D9703F",
    "grav-leger": "#E9B48A",
    "data-neutre": "#7D8A99",
    "data-neutre-clair": "#C3CAD3",
    "delta-baisse": "#2F7D5C",
    "delta-hausse": "#B3261E",
    "seq-na": "#E4E1DA",
    "on-image": "#FFFFFF",
}
DARK = {
    "bg-page": "#0E1217",
    "bg-surface": "#161B22",
    "bg-subtle": "#1E252E",
    "border": "#2A323D",
    "text-primary": "#ECEEF1",
    "text-secondary": "#A6AEB9",
    "text-muted": "#6E7783",
    "accent": "#F2B705",
    "accent-text": "#F2B705",
    "grav-tue": "#E5484D",
    "grav-hospi": "#E8834F",
    "grav-leger": "#C9956C",
    "data-neutre": "#8E99A6",
    "data-neutre-clair": "#4E5864",
    "delta-baisse": "#3FA37A",
    "delta-hausse": "#E5484D",
    "seq-na": "#232A33",
    "on-image": "#FFFFFF",
}
SEQ = {
    "light": ["#F3E9DF", "#EBC3A8", "#DC8A68", "#B8493A", "#7A1712"],
    "dark": ["#2A1F1D", "#5A2A24", "#93372E", "#C9473C", "#F05A4F"],
}
CAT = ["#5B7083", "#6F8FAF", "#8C9A6E", "#A68A64", "#8E7CA6", "#4F8A8B"]

# Voile de la carte héros (seul dégradé autorisé, §6.3) : couleur nuit en RGB + opacités
HERO_VOILE_RGB = (14, 18, 23)
HERO_VOILE_OPACITES = (0.15, 0.75)
SURVOL_OMBRE = "0 4px 16px rgba(0,0,0,.06)"

# --- Gammes Mantine (§2.3) --------------------------------------------------
AMBRE = ["#FFF8E1", "#FFEDB3", "#FFE082", "#FFD54F", "#F7C531", "#F2B705", "#E0A100",
         "#B88400", "#8A6100", "#5C4100"]
GRAVITE = ["#FDECEA", "#F9CFCB", "#F2A7A0", "#EA7B72", "#E5484D", "#D13A33", "#B3261E",
           "#8F1E18", "#6B1611", "#47100B"]
ARDOISE = ["#F1F3F5", "#E1E5EA", "#C3CAD3", "#A5AFBB", "#8E99A6", "#7D8A99", "#65717F",
           "#4E5864", "#38404A", "#22272E"]

# --- Typographie (§3) ---------------------------------------------------------
FONT_SERIF = "Fraunces, Georgia, serif"
FONT_SANS = "Inter, system-ui, sans-serif"
FONT_MONO = "ui-monospace, monospace"
FONTS_URL = ("https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@"
             "0,9..144,500;0,9..144,600;1,9..144,500&family=Inter:wght@400;500;600&display=swap")
TYPE = {  # token: (taille px, interligne px, police, graisse)
    "display": (64, 68, FONT_SERIF, 600),
    "h1": (36, 44, FONT_SERIF, 500),
    "h2": (22, 30, FONT_SERIF, 500),
    "kpi": (34, 38, FONT_SANS, 600),
    "body": (16, 26, FONT_SANS, 400),
    "label": (12, 16, FONT_SANS, 500),
    "caption": (12, 16, FONT_SANS, 400),
}

# --- Espacements, rayons, grille (§4) --------------------------------------
SPACE = [4, 8, 12, 16, 24, 32, 48, 64]
RADIUS = {"xs": 4, "sm": 6, "md": 12, "lg": 16, "xl": 24}
CONTENT_MAX = 1280
HEADER_H = 64
NAVBAR_W = 240
KPI_H = 200


def tokens(scheme: str) -> dict:
    """Jeu de tokens du mode ('light' ou 'dark'), séquentielle et catégorielle comprises."""
    base = dict(DARK if scheme == "dark" else LIGHT)
    for i, col in enumerate(SEQ["dark" if scheme == "dark" else "light"], start=1):
        base[f"seq-{i}"] = col
    for i, col in enumerate(CAT, start=1):
        base[f"cat-{i}"] = col
    return base
