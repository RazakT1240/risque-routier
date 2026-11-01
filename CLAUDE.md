# CLAUDE.md — « Risque routier » · application Dash Mantine premium

> Ce fichier est lu à chaque session. Il fixe la mission, les règles et l'ordre de travail.
> Les détails sont dans `docs/BRIEF_APP.md` (contenu : scènes, KPI, graphiques) et
> `docs/DESIGN_SYSTEM.md` (forme : tokens, composants, CSS). Lis les trois fichiers en entier
> avant d'écrire la moindre ligne de code.

## 1. Mission

Construire une application **Dash + Dash Mantine Components (DMC 2.8.x)**, de niveau premium,
qui raconte en **8 scènes** le risque corporel routier en France de **2019 à 2025**, du point de vue
d'un **actuaire qui présente au comité de direction d'un assureur auto** (public non spécialiste).

Message central : *le nombre d'accidents ne dit pas où est le risque ; le risque = fréquence × gravité,
et les deux ne sont pas au même endroit.* Les messages de chaque scène sont des **hypothèses** :
ce sont les données qui décident du texte final (voir garde-fou G3).

Contexte : c'est la **version portfolio** d'un projet préparé pour le Challenge Dataviz de l'Institut des
Actuaires. La version déposée au concours (un HTML unique, Quarto) est **hors périmètre** ici, mais
`pipeline/` et `design/` doivent rester indépendants de Dash pour pouvoir être réutilisés.

## 2. Documents de référence

| Fichier | Rôle |
| --- | --- |
| `docs/BRIEF_APP.md` | Scènes, KPI, graphiques, cartes, simulateur, textes : le **quoi** |
| `docs/DESIGN_SYSTEM.md` | Couleurs, typo, composants, CSS, template Plotly : le **comment ça doit avoir l'air** |
| `LISEZMOI.txt` | Inventaire des données et pièges connus |
| `docs/description-des-bases-de-donnees-annuelles.pdf` | **Source de vérité des codes BAAC** (grav, catv, catr, lum, atm…) |
| `docs/meteo_descriptif_champs.csv` | Champs Météo-France |
| `docs/sdes_note_methodologique_parc.pdf` | Méthodo du parc de véhicules |

## 3. Garde-fous — NON NÉGOCIABLES

**Données et chiffres**
- **G1. Aucun chiffre inventé.** Tout nombre affiché est calculé depuis les données. Pas de valeur
  « plausible », pas d'exemple en dur. Une donnée manquante → `—` + infobulle « Donnée indisponible ».
- **G2. Les codes BAAC se vérifient dans le PDF officiel** (`docs/description-...pdf`) avant d'écrire un
  mapping. Les tables de codes de `docs/BRIEF_APP.md` sont un point de départ à **confirmer**, pas une vérité.
  En cas d'écart, le PDF gagne et tu signales l'écart dans ton compte rendu.
- **G3. Les titres-messages sont générés depuis les données.** Chaque scène a un message-hypothèse ;
  si les chiffres le contredisent, tu écris le constat réel et tu le signales. Jamais de titre qui ment.
- **G4. Contrôle de cohérence obligatoire** : le nombre de tués par an calculé depuis `usagers` doit être
  reporté dans `reports/controles.md` avec le nombre d'accidents et de victimes par an. Le propriétaire du
  projet les comparera aux bilans ONISR. Si une année s'écarte fortement des autres (hors 2020), arrête-toi.
- **G5. Des taux, pas des comptages** dès qu'on compare des territoires, des âges ou des usagers :
  toujours rapporter à une exposition (population INSEE de la même année, ou parc SDES).
- **G6. Petits effectifs** : un taux calculé sur moins de 30 victimes n'est pas affiché (grisé + mention
  « effectif trop faible »). Le seuil est une constante unique dans `pipeline/config.py`.
- **G7. Les données brutes ne sont jamais modifiées.** `data/` (baac, meteo, insee, sdes, geo) est en lecture
  seule ; tout produit dérivé va dans `data/processed/` (Parquet).
- **G8. Valeurs externes non fournies** (valeurs tutélaires du coût d'un tué/blessé, part de trafic des 2RM) :
  elles vont dans `config/references.yaml` avec un champ `source` ; tant qu'elles valent `null`, tout ce qui
  en dépend affiche « À renseigner » au lieu d'un nombre. Ne les cherche pas de mémoire.

**Design**
- **G9. Aucune couleur en dur dans les composants.** Tout passe par `design/tokens.py` (Python) et les
  variables CSS de `app/assets/custom.css`. Un `#` hexadécimal hors de ces deux fichiers = bug.
- **G10. Une seule couleur d'alerte** (rouge gravité) par graphique, réservée à ce que le titre désigne ;
  tout le reste en neutre. Pas de palette arc-en-ciel.
- **G11. Interdits** : camembert > 3 parts, 3D, double axe Y, dégradés décoratifs, ombres lourdes,
  animations sans signification, emojis dans l'interface, texte en anglais dans l'interface.
- **G12. Accessibilité** : contraste AA, focus clavier visible, aucune information portée par la seule
  couleur (toujours ▲▼ ou un libellé), `prefers-reduced-motion` respecté.

**Code et méthode**
- **G13. Ne devine pas l'API DMC.** DMC change entre versions majeures. En cas de doute sur un composant
  ou une prop : lis la doc officielle (dash-mantine-components.com) pour la version installée ou
  `help(dmc.Composant)`. Pas de prop inventée.
- **G14. Pas de nouvelle dépendance** hors de la liste de la section 4 sans demander.
- **G15. Pas de calcul lourd dans les callbacks.** Les callbacks lisent des Parquet pré-agrégés, filtrent
  et tracent. Le pipeline fait tout le reste.
- **G16. Pas de secret, pas de donnée dans git** : `.gitignore` exclut `data/`, `.venv/`, `__pycache__/`.
- **G17. Travail par phases** (section 6) : à la fin de chaque phase, tu t'arrêtes, tu exécutes les
  vérifications de la phase et tu fais un compte rendu court (fait / vérifié / doutes / questions).
  Tu ne passes à la phase suivante qu'après validation.
- **G18. Supprimer est interdit sans accord** (fichiers, données, branches). Préférer déplacer.

## 4. Stack

- Python 3.11+, environnement `.venv` à la racine.
- `pandas` + `pyarrow` (Parquet), `numpy`, `openpyxl` (INSEE), `pyyaml`
- `statsmodels` (GLM Poisson et logistique)
- `dash` (dernière version stable), `dash-mantine-components` 2.8.x, `dash-iconify` (icônes Tabler : `tabler:*`),
  `plotly`, `dash-ag-grid` (page Données uniquement), `flask-caching`
- `pytest`, `ruff`
- Après installation, **figer** les versions exactes dans `requirements.txt`.
- Polices : Fraunces + Inter (Google Fonts, voir DESIGN_SYSTEM §3). Icônes : Tabler via `DashIconify`.

## 5. Arborescence cible

```
Concours_Dataviz/
├── CLAUDE.md · LISEZMOI.txt · requirements.txt · .gitignore
├── config/
│   └── references.yaml        # valeurs externes sourcées (G8), null par défaut
├── data/                      # BRUT, lecture seule (G7)
│   ├── baac/<année>/{caract,lieux,vehicules,usagers}-<année>.csv
│   ├── meteo/  insee/  sdes/  geo/
│   └── processed/             # Parquet générés par le pipeline
├── docs/                      # brief, design system, notices officielles
├── pipeline/
│   ├── config.py              # chemins, années, seuils (SEUIL_EFFECTIF=30), codes
│   ├── load.py                # lecture brute + corrections des pièges
│   ├── prepare.py             # table usager enrichie
│   ├── indicators.py          # agrégats par scène -> Parquet
│   ├── models.py              # GLM (météo, simulateur) -> coefficients JSON
│   └── run.py                 # `python -m pipeline.run` : tout reconstruire
├── design/
│   ├── tokens.py              # SOURCE UNIQUE des valeurs visuelles
│   ├── theme.py               # thème MantineProvider généré depuis tokens
│   └── plotly_template.py     # templates "route_clair" / "route_sombre"
├── app/
│   ├── app.py                 # Dash(use_pages=True), MantineProvider, AppShell
│   ├── data_access.py         # lecture Parquet + cache
│   ├── components/            # hero, kpi_card, chart_card, insight, scene_header, nav, filters
│   ├── pages/                 # s01_accueil.py … s08_methode.py
│   └── assets/                # custom.css, image héros, favicon
├── sandbox/                   # chaque composant seul avec données factices (phase 3)
├── reports/controles.md       # contrôles de cohérence (G4)
└── tests/                     # pytest : contrats de données + composants
```

## 6. Phases de travail (s'arrêter à chaque fin de phase — G17)

**Phase 0 — Mise en place**
- `.venv`, installation, `requirements.txt` figé, `.gitignore`, `git init`.
- Script d'inventaire : pour chaque fichier de `data/`, nombre de lignes, colonnes, encodage, séparateur.
- Fini quand : l'inventaire tourne et confirme les pièges listés dans `LISEZMOI.txt`.

**Phase 1 — Pipeline de données** (voir BRIEF §2 et §3)
- Lecture, corrections, table usager enrichie, agrégats Parquet, GLM.
- Tests `pytest` « contrat de données » : clés uniques, pas de doublon de `Num_Acc` dans `lieux` dédoublonné,
  `grav` ∈ {1,2,3,4}, départements à 2 caractères ou 2A/2B/97x, années 2019–2025 toutes présentes,
  population > 0 pour chaque département-année, aucun taux calculé sous le seuil.
- `reports/controles.md` rempli (G4).
- Fini quand : `python -m pipeline.run` tourne de bout en bout et `pytest` est vert.

**Phase 2 — Design system**
- `design/tokens.py`, `design/theme.py`, `design/plotly_template.py`, `app/assets/custom.css`
  strictement d'après `docs/DESIGN_SYSTEM.md`.
- Fini quand : une page de démonstration `sandbox/tokens_demo.py` affiche couleurs, typos, boutons dans
  les deux modes, et `grep` ne trouve aucun hexadécimal hors des fichiers autorisés (G9).

**Phase 3 — Composants isolés** (méthode « composants en isolation »)
- Hero, KPI retournable, carte graphique, encart insight, en-tête de scène, header, navbar, filtres.
- Chacun dans `sandbox/` avec des données factices clairement marquées « factice ».
- Fini quand : chaque composant se lit seul, en clair et en sombre, à 1440 et 390 px.

**Phase 4 — Scènes** (une scène = un commit)
- Ordre : 02 → 03 → 04 → 05 → 06 → 01 → 07 → 08 (l'accueil se fait quand les chiffres sont fiables).
- Chaque scène suit l'anatomie : en-tête → rangée de KPI → 1 ou 2 cartes graphiques → encart « Et alors ? »
  → navigation précédente / suivante.
- Fini quand : la scène respecte BRIEF + DESIGN, réagit aux filtres, n'a aucune erreur de callback.

**Phase 5 — Finitions et contrôle qualité**
- Checklist de la section 8, performances, responsive, accessibilité, mode sombre.
- `README.md` (installation, lancement, sources, limites) et capture d'écran de chaque scène dans `reports/`.

## 7. Commandes

```
python -m pipeline.run        # reconstruit data/processed/
pytest -q                     # tests
ruff check .                  # style
python app/app.py             # lance l'app en local (debug=True pendant le dev)
```

## 8. Définition de « terminé » (à cocher avant de déclarer une phase finie)

- [ ] Aucun chiffre en dur, aucun texte de remplissage dans l'interface (G1)
- [ ] Chaque titre-message reflète les données (G3)
- [ ] Taux rapportés à une exposition, seuil d'effectif appliqué (G5, G6)
- [ ] Zéro hexadécimal hors `tokens.py` / `custom.css` (G9)
- [ ] Une seule couleur d'alerte par graphique (G10)
- [ ] Mode clair et sombre corrects, y compris les figures Plotly
- [ ] Navigation clavier complète, focus visible, contrastes AA
- [ ] Rendu vérifié à 1440, 1024 et 390 px
- [ ] Premier affichage < 2 s, changement de filtre < 300 ms
- [ ] Aucune erreur dans la console du navigateur ni dans le terminal
- [ ] Sources et définitions sous chaque graphique
- [ ] `pytest` vert, `ruff` propre

## 9. Conventions

- Code et noms de variables en anglais ou français cohérent par fichier ; **interface 100 % en français**.
- Nombres affichés au format français : espace pour les milliers, virgule décimale, `%` précédé d'une espace
  insécable (`12,4 %`). Une fonction unique `fmt_number()` / `fmt_pct()` dans `app/components/format.py`.
- Une fonction = une responsabilité ; composants = fonctions Python qui renvoient des composants DMC.
- Pas de `print` de débogage laissé dans le code ; `logging` à la place.
- Messages de commit : `phase-X: <ce qui a été fait>`.

## 10. Développement « en direct » (le propriétaire regarde l'app se construire)

- Dès la phase 2, lancer l'app **en arrière-plan** et la laisser tourner : `python app/app.py`
  avec `app.run(debug=True, dev_tools_hot_reload=True, port=8050)`. Donner l'URL `http://127.0.0.1:8050`.
- Le rechargement à chaud suffit : ne pas relancer le serveur à chaque modification (seulement si une
  erreur l'a arrêté ou si une dépendance a changé).
- Pendant les phases 3 et 4, travailler **une modification visible à la fois** (un composant, une carte) et
  dire en une ligne ce qui vient de changer à l'écran.
- Si le serveur plante : lire la trace, corriger, relancer, puis signaler la cause en une phrase.
