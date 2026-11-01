# PROGRESS — à relire en premier en cas de reprise

Mode autonome (consigne du propriétaire) : G17 remplacé par une porte de qualité à chaque phase
(pytest, ruff, pipeline, app, recherche d'hexadécimaux, captures playwright, relecture par sous-agent,
reports/phase-X.md, commit). Tous les autres garde-fous s'appliquent.

## Phase en cours : 3 — Composants isolés

### Fait
- Phase 0 : `.venv` (Python 3.13.9), requirements figés, .gitignore, git init, `pipeline/inventaire.py`
  -> reports/inventaire.md ; commit 6e6ed1a.
- Phase 1 : config.py, load.py, prepare.py, indicators.py, models.py, run.py écrits ;
  `python -m pipeline.run` tourne (environ 100 s) ; reports/controles.md rempli (G4 OK).

- Phase 1 franchie (commit phase-1), rapport reports/phase-1.md.
- Phase 2 franchie (commit phase-2), rapport reports/phase-2.md.
- Phase 3 commencée : app/components/{format,kpi_card,chart_card,blocks,shell}.py, app/scenes.py,
  app/assets/app.js, design/hero.py (-> app/assets/hero-route-nuit.svg).

### Reste (phase 3)
- [ ] sandbox/components_demo.py (données factices marquées)
- [ ] captures 1440/390 clair/sombre + correction
- [ ] relecture sous-agent, reports/phase-3.md, commit

### Astuces
- Captures : démo en DASH_QA=1 ; `MSYS_NO_PATHCONV=1 .venv/Scripts/python sandbox/qa_screens.py <url> <dossier> nom=/chemin`.
- Arrêter un serveur : seulement le processus dont la ligne de commande correspond (pas de taskkill global).

### Phases suivantes
- 2 Design system · 3 Composants · 4 Scènes (02→03→04→05→06→01→07→08) · 5 Finitions

## Décisions : voir reports/DECISIONS.md
