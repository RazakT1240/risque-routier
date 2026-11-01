# Contrôles de cohérence (G4)

Généré par `python -m pipeline.run`. À comparer aux bilans ONISR de chaque année.

Définitions : victime = tué + blessé hospitalisé + blessé léger ; tué = décès dans les 30 jours ; `grav manquante` = gravité non renseignée (usagers en fuite) ; `en fuite` = usager à partir de 2021 sans sexe ni année de naissance.

## France entière (métropole + outre-mer)

| Année | Accidents | Usagers | Victimes | Tués | Hospitalisés | Légers | Létalité (tués/100 vict.) | Grav. manquante | En fuite |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2019 | 58840 | 132977 | 77663 | 3498 | 20858 | 53307 | 4.5 | 0 | 0 |
| 2020 | 47744 | 105295 | 62028 | 2780 | 16775 | 42473 | 4.48 | 0 | 0 |
| 2021 | 56518 | 129248 | 74045 | 3219 | 19093 | 51733 | 4.35 | 60 | 3060 |
| 2022 | 55302 | 126662 | 72791 | 3550 | 19260 | 49981 | 4.88 | 241 | 2742 |
| 2023 | 54822 | 125789 | 72272 | 3398 | 19271 | 49603 | 4.7 | 118 | 2422 |
| 2024 | 54402 | 125187 | 72267 | 3432 | 19126 | 49709 | 4.75 | 0 | 2390 |
| 2025 | 55093 | 126376 | 73099 | 3515 | 19601 | 49983 | 4.81 | 0 | 2218 |

## France métropolitaine

| Année | Accidents | Usagers | Victimes | Tués | Hospitalisés | Légers | Létalité (tués/100 vict.) | Grav. manquante | En fuite |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2019 | 56016 | 126352 | 73734 | 3244 | 19609 | 50881 | 4.4 | 0 | 0 |
| 2020 | 45121 | 99169 | 58377 | 2541 | 15600 | 40236 | 4.35 | 0 | 0 |
| 2021 | 53540 | 122189 | 70001 | 2944 | 17852 | 49205 | 4.21 | 54 | 2908 |
| 2022 | 52380 | 119638 | 68697 | 3267 | 18024 | 47406 | 4.76 | 215 | 2610 |
| 2023 | 51641 | 118197 | 67841 | 3167 | 18051 | 46623 | 4.67 | 96 | 2278 |
| 2024 | 51058 | 117278 | 67728 | 3193 | 17831 | 46704 | 4.71 | 0 | 2240 |
| 2025 | 51837 | 118694 | 68629 | 3263 | 18345 | 47021 | 4.75 | 0 | 2071 |

## Stabilité des tués (métropole, hors 2020)

Médiane : 3218 ; écart max toléré : 15%.

- 2019 : 3244 (+0.8%)
- 2020 : 2541 (-21.1%)
- 2021 : 2944 (-8.5%)
- 2022 : 3267 (+1.5%)
- 2023 : 3167 (-1.6%)
- 2024 : 3193 (-0.8%)
- 2025 : 3263 (+1.4%)

## Modèles

- Météo : 245449 département-jours, dispersion 1.11.
- Simulateur : 808132 usagers, taux observé de blessure grave 0.1818.
