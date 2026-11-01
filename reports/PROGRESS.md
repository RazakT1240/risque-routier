# PROGRESS — à relire en premier en cas de reprise

Mode autonome (consigne du propriétaire) : G17 remplacé par une porte de qualité à chaque phase
(pytest, ruff, pipeline, app, recherche d'hexadécimaux, captures playwright, relecture par sous-agent,
reports/phase-X.md, commit). Tous les autres garde-fous s'appliquent.

## Phase en cours : 4 — Scènes

### Fait
- Phase 0 : `.venv` (Python 3.13.9), requirements figés, .gitignore, git init, `pipeline/inventaire.py`
  -> reports/inventaire.md ; commit 6e6ed1a.
- Phase 1 : config.py, load.py, prepare.py, indicators.py, models.py, run.py écrits ;
  `python -m pipeline.run` tourne (environ 100 s) ; reports/controles.md rempli (G4 OK).

- Phase 1 franchie (commit phase-1), rapport reports/phase-1.md.
- Phase 2 franchie (commit phase-2), rapport reports/phase-2.md.
- Phase 3 commencée : app/components/{format,kpi_card,chart_card,blocks,shell}.py, app/scenes.py,
  app/assets/app.js, design/hero.py (-> app/assets/hero-route-nuit.svg).

- Phase 3 franchie (commit phase-3), rapport reports/phase-3.md.
- Phase 4 commencée : app/app.py (filtres URL/session, progression), app/data_access.py,
  app/figures.py, app/components/scene_utils.py, app/pages/s02_vue_ensemble.py (à vérifier).

### Reste (phase 4)
- [x] 02 · 03 · 04 · 05 · 06 · 01 · 07 · 08 : écrites, un commit par scène
- [x] QA filtres : sandbox/qa_filtres.py (8 pages × 5 filtres) sans erreur
- [x] Captures reports/screens/phase-4/
- [ ] Relecture sous-agent phase 4 (en cours) -> corrections
- [ ] reports/phase-4.md + commit

### Serveur
- App : `DASH_QA=1 .venv/Scripts/python app/app.py` -> http://127.0.0.1:8050 ; les nouvelles pages
  exigent un redémarrage (arrêter seulement le processus dont la ligne de commande contient app/app.py).

### Constats chiffrés (G3) déjà établis
- 02 : tués 2025 = 3 263 (indice 100,6 vs 2019) ; victimes −7 %.
- 03 : 63,5 % des accidents en agglo, 67,7 % des tués hors agglo ; létalité 7,5 vs 2,5 (× 3,0) ;
  départementales 38 % des accidents / 61 % des tués ; vma 80 létalité 10,2 ; nuit non éclairée 9,1 ; arbre 16,8.
- 04 : pic H 20-24 ans 110 graves / 100 000 ; ratio H/F tués par habitant 3,7 ; 2RM 22 % des tués,
  gravité 37,6 % (la plus haute des grands groupes) ; 51 % des piétons tués ont 65 ans et plus.
- 05 : tués / million cumul : 04 Alpes-de-Haute-Provence 101 vs 92 Hauts-de-Seine 14 (× 7,3) ;
  corrélation victimes/tués par département ≈ 0 ; nuits de week-end létalité 7,3 vs 4,6 ;
  météo : pluie RR 0,93 (moins d'accidents), première pluie n.s.
- 06 : victimes EDP +403 %, vélo +16 %, voiture −8 %, 2RM −20 % (2019→2025) ; 4 segments = 75 % des
  tués + hospitalisés.

### Astuces
- Captures : démo en DASH_QA=1 ; `MSYS_NO_PATHCONV=1 .venv/Scripts/python sandbox/qa_screens.py <url> <dossier> nom=/chemin`.
- Arrêter un serveur : seulement le processus dont la ligne de commande correspond (pas de taskkill global).

### Phases suivantes
- 2 Design system · 3 Composants · 4 Scènes (02→03→04→05→06→01→07→08) · 5 Finitions

## Décisions : voir reports/DECISIONS.md
