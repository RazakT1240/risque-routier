# Phase 2 — Design system

## Fait
- `design/tokens.py` : source unique (couleurs clair/sombre, séquentielles, catégorielles, gammes Mantine,
  typographie, espacements, rayons, palette de l'illustration du héros).
- `design/theme.py` : thème MantineProvider généré depuis les tokens (clés vérifiées en DMC 2.8.1).
- `design/plotly_template.py` : templates `route_clair` / `route_sombre`.
- `app/assets/custom.css` : variables des deux modes, alignement des variables Mantine, classes de
  composants (KPI retournable, encart, carte graphique, header, navbar, héros), focus, reduced-motion.
- `sandbox/tokens_demo.py` : page de démonstration (couleurs, typos, boutons, contrôles, figure factice).
- `sandbox/qa_screens.py` : captures playwright (clair/sombre × 1440/390) + console navigateur.
- `tests/test_design.py` : G9 automatisé (hexadécimaux 3/4/6/8 chiffres, rgb/rgba/hsl hors fichiers
  autorisés), cohérence tokens ↔ CSS (deux modes, séquentielles, voile, ombre, rayons), gammes à 10 nuances.
- Note : les premiers fichiers de cette phase ont été embarqués par erreur dans le commit de la phase 1.

## Vérifications
| Vérification | Résultat |
| --- | --- |
| `pytest -q` | 42 passés |
| `ruff check .` | propre |
| `python -m pipeline.run` | OK (phase 1, inchangé) |
| Démo qui démarre sans erreur de callback | OK, console navigateur : « aucune erreur » |
| Recherche d'hexadécimaux hors fichiers autorisés | 0 (test `test_aucun_hexadecimal_hors_fichiers_autorises`) |
| Captures | `reports/screens/phase-2/tokens_demo_{light,dark}_{1440,390}.png`, relues |

## Relecture indépendante : défauts corrigés
- **B1** : variables Mantine non surchargées (spécificité) → sélecteur `html:root[data-mantine-color-scheme=…]`
  + gamme `gray` chaude ; pistes, désactivés et texte atténué passent aux tons papier.
- **B2** : `text-muted` sous AA → #646A73 (clair) et #8A939F (sombre), ≥ 4,5:1 sur les trois fonds (G12 prime
  sur la valeur de DESIGN §2.1 ; voir DECISIONS).
- **I3** : anneau de focus `--focus-ring` (accent-text en clair 5,0:1, accent en sombre 10:1), y compris
  `.mantine-focus-auto`.
- **I4** : rouge sombre `grav-tue` / `delta-hausse` → #EE6266 (4,8–5,9:1, petit texte AA).
- **I5** : `rgba(0,0,0,0)` → token `TRANSPARENT` ; regex G9 élargie.
- **I6** : SegmentedControl à 390 px : protection CSS (pas de débordement) ; dans les scènes, un `Select`
  remplacera la bascule sous 768 px.
- **I7** : surcharges de boutons limitées aux classes `.btn-precedent` / `.btn-suivant` ; la variante
  `light` ambre utilise `--mantine-color-ambre-light-color = accent-text` (5,5:1).
- **M8** : `accent-soft`, `focus-ring` ajoutés aux tokens et testés ; séquentielles, voile, ombre, rayons testés.
- **M11** : séparateur de milliers Plotly = espace insécable.
- **M13** : captures renommées `tokens_demo_*` (anciennes déplacées dans `_to_delete/`, G18).

## Défauts mineurs restants
- M9 : `MANTINE_DARK` et `MANTINE_GRAY` contiennent des teintes intermédiaires absentes de DESIGN §2.3
  (documentées dans DECISIONS).
- M10 : `autoContrast` donne un texte noir pur sur l'ambre (9,3:1) au lieu de `text-primary`.
