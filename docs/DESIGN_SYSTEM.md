# DESIGN_SYSTEM.md — « Route de nuit »

> La **forme** de l'application. Toutes les valeurs ci-dessous sont transcrites UNE fois dans `design/tokens.py`
> et `app/assets/custom.css`, puis référencées par leur nom partout ailleurs (garde-fou G9).
> Inspiration assumée : la méthode et les détails de Gus Bavia (*The World of Peaches*, Power BI World Championship 2026),
> adaptés à un récit actuariel. On reprend l'esprit, jamais ses visuels.

## 1. Direction artistique

**« Route de nuit »** : éditorial, sobre, grave. Un fond papier (clair) ou nuit (sombre), une serif élégante pour les titres,
une sans-serif nette pour les chiffres, **un seul rouge** réservé à la gravité, **un ambre** réservé à l'interaction.
Ce qu'on veut entendre du jury : « on dirait un produit », pas « on dirait un tableau de bord Plotly ».

Sept principes :
1. Une scène = une question = un message.
2. Le titre est la conclusion (« La campagne fait les morts », jamais « Répartition par route »).
3. Une seule couleur d'alerte ; tout le reste neutre.
4. Des taux, pas des comptages.
5. Trois niveaux de lecture : coup d'œil (chiffre) → lecture (graphique) → exploration (survol, verso, filtres).
6. Le calme d'abord : beaucoup d'espace, peu de bordures, mouvement seulement s'il a du sens.
7. Chaque composant est validé seul, avec des données factices, avant d'être branché.

## 2. Couleurs

### 2.1 Interface
| Token | Clair | Sombre | Rôle |
| --- | --- | --- | --- |
| `bg-page` | `#F6F4EF` | `#0E1217` | Fond de page (papier / nuit) |
| `bg-surface` | `#FFFFFF` | `#161B22` | Cartes, panneaux, header |
| `bg-subtle` | `#EDEAE3` | `#1E252E` | Survol, verso des KPI, encart insight |
| `border` | `#DEDAD1` | `#2A323D` | Contours, séparateurs, grille des graphiques |
| `text-primary` | `#1B1F24` | `#ECEEF1` | Titres, chiffres |
| `text-secondary` | `#5A6270` | `#A6AEB9` | Texte, axes |
| `text-muted` | `#8A909A` | `#6E7783` | Sources, notes |
| `accent` | `#E0A100` | `#F2B705` | Interaction : scène active, focus, curseurs, filet de progression |
| `accent-text` | `#8A6100` | `#F2B705` | Liens / texte ambre (l'ambre pur n'est jamais du texte sur fond clair) |

### 2.2 Données
| Token | Clair | Sombre | Usage |
| --- | --- | --- | --- |
| `grav-tue` | `#B3261E` | `#E5484D` | Tués ; LE segment mis en avant |
| `grav-hospi` | `#D9703F` | `#E8834F` | Blessés hospitalisés |
| `grav-leger` | `#E9B48A` | `#C9956C` | Blessés légers |
| `data-neutre` | `#7D8A99` | `#8E99A6` | Toute série non mise en avant |
| `data-neutre-clair` | `#C3CAD3` | `#4E5864` | Contexte, fond, 2020 grisé |
| `delta-baisse` | `#2F7D5C` | `#3FA37A` | Variation favorable (moins de victimes) |
| `delta-hausse` | `#B3261E` | `#E5484D` | Variation défavorable |
| `seq-1…5` | `#F3E9DF` `#EBC3A8` `#DC8A68` `#B8493A` `#7A1712` | `#2A1F1D` `#5A2A24` `#93372E` `#C9473C` `#F05A4F` | Cartes et heatmaps (du faible au fort) |
| `seq-na` | `#E4E1DA` | `#232A33` | Valeur masquée (sous le seuil) |
| `cat-1…6` | `#5B7083` `#6F8FAF` `#8C9A6E` `#A68A64` `#8E7CA6` `#4F8A8B` | mêmes | Seulement si une comparaison exige plusieurs couleurs |

**Règles** : par défaut, tout est `data-neutre` ; on passe en `grav-tue` seulement ce que le titre désigne. La couleur d'une
variation suit le **sens pour l'assureur** (moins de victimes = vert), jamais le signe seul, et s'accompagne toujours de ▲/▼.

### 2.3 Gammes Mantine (10 nuances, index 0 → 9)
```python
AMBRE   = ["#FFF8E1","#FFEDB3","#FFE082","#FFD54F","#F7C531","#F2B705","#E0A100","#B88400","#8A6100","#5C4100"]
GRAVITE = ["#FDECEA","#F9CFCB","#F2A7A0","#EA7B72","#E5484D","#D13A33","#B3261E","#8F1E18","#6B1611","#47100B"]
ARDOISE = ["#F1F3F5","#E1E5EA","#C3CAD3","#A5AFBB","#8E99A6","#7D8A99","#65717F","#4E5864","#38404A","#22272E"]
```
`primaryColor="ambre"`, `primaryShade={"light": 6, "dark": 5}`.

## 3. Typographie

- **Fraunces** (serif, 500 / 600, italique 500) : titres de scène, titres de cartes, chiffre héros.
- **Inter** (400 / 500 / 600) : tout le reste ; chiffres en `font-variant-numeric: tabular-nums`.
- Chargement : `external_stylesheets=["https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;1,9..144,500&family=Inter:wght@400;500;600&display=swap"]`
  (ou polices auto-hébergées dans `assets/fonts/` si l'app doit fonctionner hors ligne).

| Token | Taille / interligne | Police | Usage |
| --- | --- | --- | --- |
| `display` | 64 / 68 | Fraunces 600 | Chiffre de la carte héros |
| `h1` | 36 / 44 | Fraunces 500 | Titre-message de scène |
| `h2` | 22 / 30 | Fraunces 500 | Titre de carte graphique |
| `kpi` | 34 / 38 | Inter 600 tabulaire | Valeur KPI |
| `body` | 16 / 26 | Inter 400 | Chapeaux, textes |
| `label` | 12 / 16 | Inter 500, CAPITALES, interlettrage 0,08 em | Sur-titres, libellés KPI, numéros de scène |
| `caption` | 12 / 16 | Inter 400 | Sources, notes, axes |

**Touche Gus Bavia** : la seconde moitié du titre-message en **Fraunces italique, couleur `grav-tue`** :
« La ville fait les accidents, *la campagne fait les morts*. »

## 4. Espacements, formes, grille

- Base 4 px ; échelle `4 · 8 · 12 · 16 · 24 · 32 · 48 · 64`.
- Carte : padding 24 ; écart entre cartes 24 ; entre blocs de scène 48 ; texte de récit ≤ 68 caractères de large.
- Rayons : 6 (contrôles), 12 (cartes), 16 (héros). `defaultRadius="md"` avec md = 12 px dans le thème.
- Bordure 1 px `border` ; **aucune ombre au repos** ; survol carte : `0 4px 16px rgba(0,0,0,.06)` (clair seulement ;
  en sombre la surface passe à `bg-subtle`).
- Grille 12 colonnes, contenu max 1280 px centré. Icônes Tabler (`DashIconify(icon="tabler:...", width=20)`), trait fin.

## 5. Thème Mantine (`design/theme.py`)

```python
from design.tokens import AMBRE, GRAVITE, ARDOISE
THEME = {
    "primaryColor": "ambre",
    "primaryShade": {"light": 6, "dark": 5},
    "colors": {"ambre": AMBRE, "gravite": GRAVITE, "ardoise": ARDOISE},
    "fontFamily": "Inter, system-ui, sans-serif",
    "fontFamilyMonospace": "ui-monospace, monospace",
    "headings": {"fontFamily": "Fraunces, Georgia, serif", "fontWeight": "500"},
    "defaultRadius": "md",
    "radius": {"xs": "4px", "sm": "6px", "md": "12px", "lg": "16px", "xl": "24px"},
    "components": {
        "Button": {"defaultProps": {"radius": "sm", "fw": 500}},
        "Paper": {"defaultProps": {"radius": "md", "withBorder": True, "p": "lg"}},
        "NavLink": {"defaultProps": {"variant": "light"}},
        "SegmentedControl": {"defaultProps": {"radius": "sm"}},
    },
}
```
Vérifier chaque clé contre la doc DMC de la version installée (G13). Le mode clair/sombre se pilote par
`MantineProvider` (`defaultColorScheme="light"`) et un interrupteur dans le header, en suivant l'exemple officiel
« theme switch » de DMC ; l'attribut `data-mantine-color-scheme` de `<html>` sert de sélecteur au CSS ci-dessous.

## 6. Composants

### 6.1 Header (`dmc.AppShell` header, hauteur 64)
- Gauche : monogramme + « Risque routier » (Fraunces 500, 18) + sous-titre « Fréquence · Gravité · Coût » (`label`).
- Centre : « Scène 3 / 8 » (`caption`) + **filet de progression ambre** de 2 px sous tout le header, rempli au prorata de la scène.
- Droite : filtres **Période** et **Territoire** (libellé `label` au-dessus + icône calendrier / carte), interrupteur de thème.

### 6.2 Carte KPI retournable (signature)
**Recto** (dans cet ordre) :
1. `label` + icône Tabler (« TUÉS · 2025 »).
2. Valeur `kpi`.
3. Variations : « ▲ +X % vs 2024 · ▼ −X % vs 2019 », couleurs `delta-*`.
4. Ligne leader : icône du segment + « 2RM en tête : X % des tués » (toujours rapportée à une exposition quand c'est possible).
5. Mini-courbe 2019–2025 (`dmc.Sparkline` ou petite figure Plotly), neutre, dernier point `grav-tue`.
6. Indice discret en bas : icône rotation + « Survoler pour l'explication » (`text-muted`).

**Verso** : « Comment le lire » (définition, 1 phrase) · « Pour l'assureur » (1 phrase) · source / calcul en `caption`.
Fond `bg-subtle`, filet ambre 3 px à gauche. **Jamais de nouveau chiffre au verso.**

**Comportement** : survol souris, focus clavier (Tab) et Entrée/Espace, toucher mobile (classe `on` ajoutée par
`clientside_callback`). Rotation 3D 550 ms ; `prefers-reduced-motion` → bascule instantanée. `aria-label` = valeur + explication.
Hauteur fixe 200 px (les quatre cartes d'une rangée alignées).

### 6.3 Carte héros (scène 01)
Image plein cadre (rayon 16), voile `linear-gradient(180deg, rgba(14,18,23,.15), rgba(14,18,23,.75))` (seul dégradé autorisé,
fonctionnel pour la lisibilité) ; sur-titre `label`, chiffre `display` blanc, phrase « soit X par jour » en fondu après 1 s,
bouton ambre « Commencer ». Option « cinémagraphe » (gouttes, phares au loin) en boucle de 4 s, désactivée si
`prefers-reduced-motion`. Image libre de droits ou générée, créditée en pied de page.

### 6.4 Carte graphique
En-tête : titre-message `h2` + sous-titre de lecture `caption` + menu ⋯ (agrandir, télécharger PNG, voir les données) +
puce de filtre actif. Corps : **un seul** graphique. Pied : « Source : … · Définition : … » en `caption`.

### 6.5 Encart « Et alors ? »
Fond `bg-subtle`, filet ambre 3 px à gauche (coins gauche non arrondis), titre `label` « ET ALORS ? », 2 lignes `body` max.

### 6.6 En-tête de scène
`label` « 03 · LE PARADOXE » → `h1` titre-message (avec la moitié en italique rouge) → chapeau `body` `text-secondary`.

### 6.7 Navigation
`AppShell` navbar 240 px : badge en haut « Challenge Dataviz · Institut des Actuaires » ; 8 `dmc.NavLink`
(numéro + nom + icône) ; actif = fond ambre léger + barre ambre 3 px à gauche. En bas de chaque scène : boutons
« ← Scène précédente » (contour) et « Scène suivante → » (ambre léger).

### 6.8 États
Chargement : `dmc.Skeleton` à la forme exacte du composant. Vide / sous le seuil : message explicite
(« Moins de 30 victimes sur ce périmètre : taux non affiché »). Erreur : carte sobre + bouton « Réessayer ».

## 7. CSS (`app/assets/custom.css`) — à transcrire tel quel puis compléter

```css
:root{
  --bg-page:#F6F4EF;--bg-surface:#FFFFFF;--bg-subtle:#EDEAE3;--border:#DEDAD1;
  --text-primary:#1B1F24;--text-secondary:#5A6270;--text-muted:#8A909A;
  --accent:#E0A100;--accent-text:#8A6100;
  --grav-tue:#B3261E;--delta-baisse:#2F7D5C;--delta-hausse:#B3261E;
}
[data-mantine-color-scheme="dark"]{
  --bg-page:#0E1217;--bg-surface:#161B22;--bg-subtle:#1E252E;--border:#2A323D;
  --text-primary:#ECEEF1;--text-secondary:#A6AEB9;--text-muted:#6E7783;
  --accent:#F2B705;--accent-text:#F2B705;
  --grav-tue:#E5484D;--delta-baisse:#3FA37A;--delta-hausse:#E5484D;
}
body{background:var(--bg-page);color:var(--text-primary);font-feature-settings:"tnum" 1}
.label{font:500 12px/16px Inter,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:var(--text-secondary)}
.titre-accent{font-family:Fraunces,serif;font-style:italic;color:var(--grav-tue)}

/* Carte KPI retournable */
.kpi-flip{perspective:1000px;height:200px;cursor:pointer;outline:none}
.kpi-flip-inner{position:relative;width:100%;height:100%;transition:transform .55s cubic-bezier(.2,.7,.2,1);transform-style:preserve-3d}
.kpi-flip:hover .kpi-flip-inner,.kpi-flip:focus-visible .kpi-flip-inner,.kpi-flip.on .kpi-flip-inner{transform:rotateY(180deg)}
.kpi-face{position:absolute;inset:0;backface-visibility:hidden;-webkit-backface-visibility:hidden;border-radius:12px;
  border:1px solid var(--border);background:var(--bg-surface);padding:20px 22px;display:flex;flex-direction:column;gap:6px}
.kpi-back{transform:rotateY(180deg);background:var(--bg-subtle);border-left:3px solid var(--accent);border-radius:0 12px 12px 0}
.kpi-flip:focus-visible .kpi-face{box-shadow:0 0 0 2px var(--accent)}

/* Encart insight */
.insight{background:var(--bg-subtle);border-left:3px solid var(--accent);border-radius:0 12px 12px 0;padding:16px 20px}

/* Filet de progression */
.progress-rule{height:2px;background:var(--accent);transition:width .25s ease-out}

@media (prefers-reduced-motion:reduce){
  *,*::before,*::after{transition:none!important;animation:none!important}
}
```

## 8. Graphiques Plotly (`design/plotly_template.py`)

Deux templates, `route_clair` et `route_sombre`, générés depuis `tokens.py` ; chaque figure est construite avec le
template du mode courant (Plotly ne lit pas les variables CSS → le changement de thème re-déclenche les figures).

```python
import plotly.graph_objects as go
def make_template(t):  # t = jeu de tokens du mode
    return go.layout.Template(layout=dict(
        font=dict(family="Inter, sans-serif", size=13, color=t["text-secondary"]),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        colorway=[t["data-neutre"], t["data-neutre-clair"]],
        margin=dict(l=8, r=8, t=8, b=8),
        separators=", ",                      # virgule décimale, espace milliers
        xaxis=dict(showgrid=False, zeroline=False, showline=True, linecolor=t["border"],
                   ticks="outside", tickcolor=t["border"], tickfont=dict(size=12)),
        yaxis=dict(showgrid=True, gridcolor=t["border"], gridwidth=1, zeroline=False,
                   showline=False, tickfont=dict(size=12)),
        hoverlabel=dict(bgcolor=t["bg-surface"], bordercolor=t["border"],
                        font=dict(family="Inter", size=13, color=t["text-primary"])),
        legend=dict(orientation="h", y=-0.18, font=dict(size=12)),
        title=dict(text=""),                  # le titre vit dans la carte, pas dans la figure
    ))
```
- `dcc.Graph(config={"displayModeBar": False, "responsive": True})`.
- Séries temporelles : `hovermode="x unified"` ; annotations directes plutôt que légende.
- Barres : `marker_line_width=0`, rayon via `marker_cornerradius=4` si la version de Plotly le permet.
- Cartes : `go.Choropleth(geojson=..., featureidkey="properties.code", locations=dep, z=taux)`,
  `geo=dict(fitbounds="locations", visible=False, projection_type="mercator")`, contours 0,5 px `bg-surface`,
  échelle discrète `seq-1…5` par quantiles, `seq-na` pour les valeurs masquées. Pas de fond de carte tuilé.
- Heatmap : `go.Heatmap`, `xgap=2, ygap=2` (cellules séparées), échelle `seq-*`.
- Moustaches (IC) : `error_x=dict(type="data", array=..., arrayminus=..., thickness=1.25, width=4)`.

## 9. Mouvement
- Apparition des cartes et changement de filtre : 150–250 ms `ease-out`.
- Valeurs KPI : comptage animé **uniquement** au premier affichage d'une scène.
- Rotation KPI : 550 ms. Rien d'autre ne bouge. `prefers-reduced-motion` coupe tout.

## 10. Responsive
- ≥ 1200 px : navbar ouverte, KPI sur 4 colonnes, graphiques 2 colonnes.
- 768–1199 px : navbar repliée en icônes, KPI 2 × 2, graphiques 1 colonne.
- < 768 px : burger, une colonne ; cartes choroplèthes → barres classées par département ; heatmap → barres par heure.

## 11. Accessibilité
Contraste AA dans les deux modes ; focus visible (anneau ambre 2 px) ; navigation complète au clavier ; chaque graphique a un
`aria-label` qui reprend son titre-message ; aucune information portée par la seule couleur ; tailles de texte ≥ 12 px.

## 12. Les 12 touches « Gus Bavia » à ne pas oublier
1. Moitié du titre en italique rouge. 2. Filet ambre de progression sous le header. 3. Sous-titre triptyque
« Fréquence · Gravité · Coût ». 4. Badge de marque en haut de la navbar. 5. Héros photo + chiffre géant. 6. Cinémagraphe
discret (si mouvement réduit non demandé). 7. Ligne leader sous chaque KPI. 8. Double comparateur vs N−1 et vs 2019.
9. Couleur selon le sens pour l'assureur. 10. Sélecteurs libellés avec icône. 11. Page Données en tableau. 12. États des
boutons définis une fois dans le thème (`theme.components`).

## 13. Interdits (rappel G11)
Camembert > 3 parts · 3D · double axe Y · dégradés décoratifs · ombres lourdes · légende qui masque les données ·
plus d'une couleur d'alerte · emojis · texte anglais dans l'interface · couleur en dur hors tokens.
