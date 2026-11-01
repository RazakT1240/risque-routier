# Phase 4 — Scènes

## Fait
- `app/app.py` (Dash pages, MantineProvider, AppShell, filtres synchronisés avec l'URL `?annee=&dep=` et la
  session, filet de progression), `app/data_access.py` (Parquet en cache, filtres, expositions),
  `app/figures.py` (tous les types de graphiques, couleurs lues dans les tokens), `app/pages/` (8 scènes + 404).
- Une scène = un commit (02 → 03 → 04 → 05 → 06 → 01 → 07 → 08), puis un commit de corrections de relecture et un
  commit de refonte visuelle demandée par le propriétaire.
- Refonte visuelle (demande du propriétaire, avec ses références) : cartes KPI « box » épurées avec carte
  vedette, courbe annotée année par année, anneau de répartition (3 parts), jauge en anneau, matrices
  (route × lumière, mode × âge), boîtes à moustaches (âges des tués par mode, dispersion des départements sur
  7 ans), barres 100 % par année (lieu, mode avec la palette catégorielle), grande carte avec bascule et
  classement des 10 premiers.

## Titres-messages finaux (générés depuis les données, G3)
| Scène | Titre |
| --- | --- |
| 02 | Les tués ne baissent plus : *2025 retrouve le niveau de 2019.* |
| 03 | La ville fait les accidents, *la campagne fait les morts.* |
| 04 | Les jeunes hommes et les deux-roues *concentrent les blessures graves.* |
| 05 | Selon le département, le risque de mourir sur la route *varie de 1 à 7.* |
| 06 | Les victimes en trottinette ou EDP *ont été multipliées par 5 depuis 2019.* |
| 07 | Le mode de déplacement et le lieu *pèsent plus que la nuit ou la pluie.* |
| 08 | Chaque chiffre vient des données, *et se vérifie.* |

## Vérifications
| Vérification | Résultat |
| --- | --- |
| `pytest -q` | 48 passés |
| `ruff check .` | propre |
| `python -m pipeline.run` | OK (102 s), 2 agrégats ajoutés (`s03_matrice`, `s04_age_box`) |
| `sandbox/qa_filtres.py` (8 pages × 5 filtres : cumul, Lozère 2020, Paris 2019, Corse-du-Sud 2023…) | aucun problème |
| Console navigateur (captures clair / sombre × 1440 / 390) | aucune erreur |
| Hexadécimaux hors fichiers autorisés | 0 |
| Débordement / troncature des KPI (1440, 1280, 1024, 390 ; cumul + Finistère, 2025) | aucun |
| Premier affichage d'une scène | 0,8 à 1,6 s ; rechargement complet après changement de filtre ≈ 1,0 à 1,9 s |

## Relecture indépendante : défauts corrigés
- B1 titre de heatmap faux (nuits de week-end) → titre calculé (« Entre minuit et 6 h, une victime est 1,6 fois
  plus souvent tuée »).
- B2 simulateur : un rapport de cotes présenté comme un risque → risque relatif (probabilité / part observée,
  18 %) ; les rapports de cotes restent nommés comme tels dans l'encart.
- I3 « un accident 3 fois plus souvent mortel » → « une victime 3 fois plus souvent tuée ».
- I4 dénominateur explicite (« une victime en 2RM est tuée ou hospitalisée dans 38 % des cas »).
- I5 phrase non démontrée retirée (« l'âge, le sexe… l'essentiel de la gravité »).
- I6 versos sans affirmation chiffrée hors données ; part du trafic 2RM « À renseigner » (G8).
- I7 plus de doublon « vs 2019 » en 2020 ; I8 pas de variation sous une valeur indisponible.
- I9 variations des parts et de la létalité en points.
- I10 titres de cartes graphiques générés depuis les données filtrées.
- I11 heatmap mobile : heures sous le seuil grisées, « effectif trop faible » au survol.
- I12 Pareto : seuil 80 % en neutre (une seule couleur d'alerte).
- Mineurs : accents, tirets demi-cadratins, formulations, « — » quand la période vaut 2019, créneau sur des
  tranches de 3 h, libellés tronqués, légende sans « effectif trop faible » inutile, note sur les non-résidents,
  bouton « Comparer », annotation de l'écart sur la barre rouge du miroir.

## Défauts mineurs restants
- Captures pleine page : la navbar fixe s'arrête à la hauteur de la fenêtre (artefact de capture).
- Les boîtes « âge des tués » sont nationales (statistiques non additives), non filtrables par département.
- Changement de filtre mesuré en rechargement complet (≈ 1 s) ; en navigation, seuls les callbacks
  rejouent (voir phase 5).
