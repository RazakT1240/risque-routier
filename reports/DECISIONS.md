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

## Constats contraires aux hypothèses (G3)
- Scène 05, météo : la pluie est associée à **moins** d'accidents par département-jour (pluie faible RR 0,93, IC 0,93–0,94 ; pluie forte 0,93 ; gel 0,91), et « première pluie » n'a pas d'effet significatif (RR 1,01, IC 0,98–1,04). Le titre de la scène 05 ne dira donc pas que les premières pluies sont critiques.
- Taux territoriaux (scène 05) : carte et KPI calculés sur le cumul 2019–2025 (victimes cumulées / somme des populations annuelles) — par an et par département, le seuil G6 masquait la moitié des départements (relecture, B1).
- `casque` à 3 modalités (Casque / Aucun équipement / Indéterminé) — secu = 8 « non déterminable » ne doit pas compter comme « sans casque ».
- Taux par parc : groupe VP = catv 7 seulement (voiturette exclue, absente du parc VP du SDES).
