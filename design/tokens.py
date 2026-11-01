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
    "text-muted": "#646A73",
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
    "accent-soft": "rgba(224,161,0,.12)",
    "focus-ring": "#8A6100",
    "delta-baisse-soft": "rgba(47,125,92,.12)",
    "delta-hausse-soft": "rgba(179,38,30,.10)",
    "vedette-bg": "#1B1F24",
    "vedette-text": "#FFFFFF",
    "vedette-muted": "#A6AEB9",
    "vedette-hausse": "#EE6266",
    "vedette-baisse": "#3FA37A",
    "on-image": "#FFFFFF",
}
DARK = {
    "bg-page": "#0E1217",
    "bg-surface": "#161B22",
    "bg-subtle": "#1E252E",
    "border": "#2A323D",
    "text-primary": "#ECEEF1",
    "text-secondary": "#A6AEB9",
    "text-muted": "#8A939F",
    "accent": "#F2B705",
    "accent-text": "#F2B705",
    "grav-tue": "#EE6266",
    "grav-hospi": "#E8834F",
    "grav-leger": "#C9956C",
    "data-neutre": "#8E99A6",
    "data-neutre-clair": "#4E5864",
    "delta-baisse": "#3FA37A",
    "delta-hausse": "#EE6266",
    "seq-na": "#232A33",
    "accent-soft": "rgba(242,183,5,.12)",
    "focus-ring": "#F2B705",
    "delta-baisse-soft": "rgba(63,163,122,.16)",
    "delta-hausse-soft": "rgba(238,98,102,.16)",
    "vedette-bg": "#232B36",
    "vedette-text": "#ECEEF1",
    "vedette-muted": "#A6AEB9",
    "vedette-hausse": "#EE6266",
    "vedette-baisse": "#3FA37A",
    "on-image": "#FFFFFF",
}
SEQ = {
    "light": ["#FCEEE4", "#F6C7A8", "#EC8F68", "#CF4C3A", "#8C1C16"],
    "dark": ["#2A1C1B", "#5B2822", "#98372D", "#D45244", "#F77E70"],
}
CAT = ["#3E5C76", "#4F86A6", "#6A9E7F", "#C9A061", "#9A7BB0", "#3F8F8B"]

# Illustration générée du héros (route de nuit sous la pluie, design/hero.py)
HERO_PALETTE = {
    "ciel-haut": "#07090C", "ciel-horizon": "#1B2431", "halo-ville": "#3A2E1A",
    "relief": "#0B0F14", "chaussee": "#0F1318", "chaussee-loin": "#1A2029",
    "marquage": "#C9CED6", "phare": "#FFF4D6", "feu-arriere": "#E5484D",
    "reflet-ambre": "#F2B705", "pluie": "#A6AEB9",
}

# Voile de la carte héros (seul dégradé autorisé, §6.3) : couleur nuit en RGB + opacités
HERO_VOILE_RGB = (14, 18, 23)
HERO_VOILE_OPACITES = (0.15, 0.75)
SURVOL_OMBRE = "0 4px 16px rgba(0,0,0,.06)"
TRANSPARENT = "rgba(0,0,0,0)"

# --- Gammes Mantine (§2.3) --------------------------------------------------
AMBRE = ["#FFF8E1", "#FFEDB3", "#FFE082", "#FFD54F", "#F7C531", "#F2B705", "#E0A100",
         "#B88400", "#8A6100", "#5C4100"]
GRAVITE = ["#FDECEA", "#F9CFCB", "#F2A7A0", "#EA7B72", "#E5484D", "#D13A33", "#B3261E",
           "#8F1E18", "#6B1611", "#47100B"]
# Palette « dark » de Mantine (surfaces du mode sombre) alignée sur les tokens nuit :
# 0 texte, 2 atténué, 4 bordure, 5 survol, 6 contrôle, 7 surface/fond, 8-9 plus profond
MANTINE_DARK = ["#ECEEF1", "#C9CED6", "#A6AEB9", "#6E7783", "#2A323D", "#242B35", "#1E252E",
                "#161B22", "#0E1217", "#0A0D11"]
# Palette « gray » de Mantine réchauffée (fonds des contrôles sur papier, texte atténué)
MANTINE_GRAY = ["#FAF9F6", "#F2EFE9", "#EAE6DE", "#DEDAD1", "#C8C3B8", "#A29D92", "#646A73",
                "#4E4A44", "#34312D", "#1B1F24"]
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


def transparence(couleur: str, alpha: float) -> str:
    """Couleur d'un token (hexadécimal) avec une opacité, pour les remplissages."""
    c = couleur.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"
