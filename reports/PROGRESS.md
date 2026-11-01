# PROGRESS — à relire en premier en cas de reprise

Mode autonome (consigne du propriétaire) : G17 remplacé par une porte de qualité à chaque phase
(pytest, ruff, pipeline, app, recherche d'hexadécimaux, captures playwright, relecture par sous-agent,
reports/phase-X.md, commit). Tous les autres garde-fous s'appliquent.

## Phase en cours : 1 — Pipeline de données

### Fait
- Phase 0 : `.venv` (Python 3.13.9), requirements figés, .gitignore, git init, `pipeline/inventaire.py`
  -> reports/inventaire.md ; commit 6e6ed1a.
- Phase 1 : config.py, load.py, prepare.py, indicators.py, models.py, run.py écrits ;
  `python -m pipeline.run` tourne (environ 100 s) ; reports/controles.md rempli (G4 OK).

### Reste (phase 1)
- [ ] tests/test_contrats.py
- [ ] ruff, pytest
- [ ] relecture par sous-agent
- [ ] reports/phase-1.md + commit

### Phases suivantes
- 2 Design system · 3 Composants · 4 Scènes (02→03→04→05→06→01→07→08) · 5 Finitions

## Décisions : voir reports/DECISIONS.md
