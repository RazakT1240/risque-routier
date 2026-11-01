# Décisions prises en autonomie

Format : décision — justification (une ligne).

## Phase 0
- Python 3.13.9 (le seul installé hors Anaconda) pour `.venv` — conforme à « 3.11+ » du CLAUDE.md.
- `_to_delete/` exclu de git et jamais touché — consigne explicite du propriétaire.

## Phase 1
- Valeurs `" -1"` (espace en tête) et `"N/A"` littéral nettoyées à la lecture — pièges absents du LISEZMOI, découverts à l'inventaire.
- `nbv` : quelques valeurs non numériques (1 à 54 par an) mises à manquant, avec un log — variable non utilisée dans les scènes.
- Doublons de `lieux` présents seulement en 2023–2025 ; 1re ligne gardée (BRIEF §2.1.9).
- `en_fuite` = année ≥ 2021 et sexe et année de naissance manquants — c'est la signature observée ; `grav = -1` n'existe qu'en 2021–2023.
- `meteo_cat` : gel prioritaire, puis pluie forte (≥ 5 mm), pluie faible (≥ 0,2 mm), sec — le brief ne fixe pas la priorité quand gel et pluie coexistent.
- « Première pluie » : jour ≥ 1 mm après ≥ 7 jours consécutifs à < 0,2 mm (définition « sec » du brief) ; elle entre dans le GLM comme indicatrice additive en plus de `meteo_cat`.
- GLM météo en quasi-Poisson (échelle de Pearson) — des IC honnêtes en cas de surdispersion (dispersion estimée : 1,11).
- `expo_population` garde aussi les DOM présents à l'INSEE (971–974, 976), avec un indicateur `metropole` — nécessaire pour la page Données ; cartes et taux filtrent sur la métropole.
- Simulateur : le « profil moyen » est la moyenne du prédicteur linéaire sur l'échantillon (x̄·β) ; rapport de cotes = exp(η − η̄).
- Convention G6 : chaque `taux_x` est accompagné de `eff_x` ; un taux est masqué si `eff_x < SEUIL_EFFECTIF` (pour les taux de population, l'effectif est le numérateur ; pour la létalité, ce sont les victimes).
- Modèles JSON écrits dans `data/processed/models/` (hors git, régénérés par le pipeline).
- Taux territoriaux (scène 05) : carte et KPI calculés sur le cumul 2019–2025 (victimes cumulées / somme des populations annuelles) — par an et par département, le seuil G6 masquait la moitié des départements (relecture, B1).
- `casque` à 3 modalités (Casque / Aucun équipement / Indéterminé) — secu = 8 « non déterminable » ne doit pas compter comme « sans casque ».
- Taux par parc : groupe VP = catv 7 seulement (voiturette exclue, absente du parc VP du SDES).

## Phase 2
- `text-muted` : #646A73 (clair) et #8A939F (sombre) au lieu de #8A909A / #6E7783 — DESIGN §2.1 échouait AA (2,7–3,8:1) ; G12 est non négociable.
- Rouge du mode sombre (`grav-tue`, `delta-hausse`) : #EE6266 au lieu de #E5484D — 3,95:1 sur bg-subtle, insuffisant pour le petit texte des variations.
- Gammes Mantine `dark` et `gray` dérivées des tokens (teintes intermédiaires ajoutées) — sans cela Mantine affiche ses gris froids par défaut.
- Anneau de focus = `accent-text` en clair (l'ambre pur ne fait que 2,1:1 sur papier), `accent` en sombre.
- Illustration du héros générée en SVG par `design/hero.py` depuis `tokens.HERO_PALETTE` — pas de photo fournie, aucun droit tiers, cohérent avec G9 ; pluie animée (4 s) seulement sans mouvement réduit.
- Retournement des KPI au clic / clavier par un script d'assets (`app/assets/app.js`) plutôt qu'un clientside_callback — même effet, sans aller-retour ni identifiant par carte.
- Mini-courbes KPI : `dmc.Sparkline` en `var(--data-neutre)` + pastille `grav-tue` superposée pour le dernier point — suit le thème sans re-rendu.

## Phase 4
- Scène 04, matrice : axe Y = taux de gravité (tués + hospitalisés) / victimes au lieu de la létalité — en létalité, les 2RM (4,0) passent sous la voiture (4,9) ; le taux de gravité est un indicateur du BRIEF §3 et fait ressortir le constat réel (2RM 37,6 % vs voiture 27,9 %).
- Scène 04, matrice : type « Autre » (quads, engins, tracteurs) exclu — catégorie hétérogène sans lecture tarifaire.
- Scène 04, KPI 3 : la ligne leader donne la létalité des 2RM « sans équipement » (secu = 0) seulement si l'effectif ≥ 30 ; « Indéterminé » n'est pas compté comme sans casque.
- Parts et rapports (part des accidents en agglo, ratio H/F, part des 2RM…) : variations affichées en neutre — ni favorables ni défavorables pour l'assureur ; les ▲▼ restent.
- Titres-messages : générés au chargement depuis les données nationales cumulées ; les KPI et graphiques suivent les filtres.
- Séparateur de milliers : espace insécable U+00A0 (et non l'espace fine U+202F, quasi invisible à l'écran dans Inter) — même séparateur que les figures Plotly.
- Simulateur : la jauge et la phrase affichent un risque relatif (probabilité du profil / part observée de blessés graves, 18 %) et non un rapport de cotes présenté comme un risque (relecture, B2) ; les rapports de cotes restent cités comme tels dans l'encart. Bouton « Comparer à la moyenne » au lieu d'un interrupteur (BRIEF : bouton).
- Variations des parts et des taux pour 100 (létalité) affichées en points (« ▲ +0,8 pt ») ; comptages et taux par habitant en % relatif.
- Titres des cartes graphiques générés depuis les données filtrées (ou neutres quand aucun constat ne s'impose) ; le titre-message de scène reste national.
- Créneau le plus létal (scène 05) : tranches de 3 h (une case jour × heure isolée est trop bruitée).
- Matrice de la scène 04 : parts de victimes calculées sur tous les types avant d'écarter « Autre » et les types sous le seuil.
- Textes « Pour l'assureur » : aucune affirmation chiffrée hors données ; part des 2RM dans le trafic citée comme « À renseigner » (G8).
- Liens des sources (page Méthode) : domaines officiels seulement (pas d'URL de jeu de données citée de mémoire).

## Constats contraires aux hypothèses (G3)
- Scène 05, météo : la pluie est associée à **moins** d'accidents par département-jour (pluie faible RR 0,93, IC 0,93–0,94 ; pluie forte 0,93 ; gel 0,91), et « première pluie » n'a pas d'effet significatif (RR 1,01, IC 0,98–1,04). Le titre de la scène 05 ne dira donc pas que les premières pluies sont critiques.
- Scène 04 : la létalité des 2RM (4,0 tués / 100 victimes) est inférieure à celle des occupants de voiture (4,9) ; c'est sur le taux de gravité que les 2RM ressortent.
- Scène 05 : les cases les plus létales sont des nuits de semaine (mercredi 3 h sur le cumul), pas seulement de week-end ; le titre de la heatmap est désormais calculé (« Entre minuit et 6 h, une victime est X fois plus souvent tuée »).
- Scène 05 : le titre ne parle plus de « départements ruraux » (non calculé) mais de l'écart mesuré entre départements (de 1 à 7).
