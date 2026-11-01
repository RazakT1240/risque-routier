# Phase 1 — Pipeline de données

## Fait
- `pipeline/config.py` (chemins, années, `SEUIL_EFFECTIF = 30`, codes vérifiés dans le PDF ONISR p. 4-13),
  `load.py` (12 corrections du BRIEF §2.1 et 2 pièges en plus : espaces en tête, `N/A`),
  `prepare.py` (usagers enrichis, accidents, expositions, météo catégorisée + première pluie),
  `indicators.py` (formules uniques, `masque_seuil`, 14 agrégats Parquet), `models.py` (GLM météo,
  logistique du simulateur), `run.py` (orchestration + `reports/controles.md`).
- `python -m pipeline.run` : 67 s de bout en bout, 19 Parquet + 2 JSON dans `data/processed/`.

## Vérifications
| Vérification | Résultat |
| --- | --- |
| `python -m pipeline.run` | OK, 67 s |
| `pytest -q` | 36 passés |
| `ruff check .` | propre |
| G4 tués / an (métropole, hors 2020) | écart max −8,5 % (2021) vs médiane 3 218 ; seuil 15 % : OK |
| Jointures | 871 534 usagers en entrée = en sortie (test `test_aucun_usager_perdu`) |

## Relecture indépendante (sous-agent) : défauts corrigés
- **B1 (bloquant)** : tués par million par département et par an, sous le seuil, masquait la moitié des
  départements, ruraux surtout. Ajout de `ind_territoires` (années + cumul 2019–2025, personnes-années) ;
  la carte et les KPI territoriaux de la scène 05 utiliseront le cumul.
- **I1** : `casque` passe à 3 modalités (Casque / Aucun équipement / Indéterminé) au lieu d'un booléen qui
  rangeait les « non déterminable » parmi les sans casque.
- **I2** : formules et `masque_seuil` testées (`tests/test_indicateurs.py`) ; l'app les importera depuis
  `pipeline.indicators` (une seule définition).
- **M1** : la météo est réindexée sur un calendrier complet avant le calcul de « première pluie ».
- **M2** : voiturette (catv 3) retirée du groupe VP pour le taux par parc.
- **M3** : `actp` « -1 » et « 0 » mis à manquant.
- **M4** : `premiere_pluie` en `Int8`.
- **M5** : tests ajoutés (années et départements sur chaque agrégat, couverture GeoJSON, aucun usager
  perdu, population fine, cohérence des tués entre scènes, cumul territoires, casque).
- **M6** : `accidents_mortels` vectorisé.

## Défauts mineurs restants
- M7 : le BRIEF §1 indique 58 841 accidents en 2019 et 47 745 en 2020 ; le calcul donne 58 840 et 47 744
  (probablement la ligne d'en-tête comptée dans le brief). Pas de correction de code.

## Décisions et doutes
- Voir `reports/DECISIONS.md` (phase 1).
- **Constat G3** : la pluie est associée à moins d'accidents par département-jour (RR 0,93) et « première
  pluie » n'a pas d'effet significatif ; le titre de la scène 05 en tiendra compte.
- Les hospitalisés (environ 18 000 / an en métropole) : indicateur non labellisé depuis 2019 (mention en scène 08).
