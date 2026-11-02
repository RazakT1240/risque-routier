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

## Phase 4 — refonte visuelle demandée par le propriétaire
- Cartes KPI épurées à la demande du propriétaire (« trop d'info ») : recto = libellé, valeur, UNE variation (vs N−1), mini-courbe ; la ligne leader passe au verso, la source en infobulle de la carte (elle reste sous chaque graphique et en page Méthode). Écart assumé à DESIGN §6.2 et §12 (touches 7 et 8).
- Première carte de chaque rangée en « vedette » (fond encre) — hiérarchie visuelle, sans dégradé.
- Mini-courbes : série décalée pour occuper la hauteur (Recharts part de zéro) ; seule la forme est lue, aucune valeur.
- Nouveaux graphiques : courbe annotée année par année (creux / pic, variation annuelle), anneau de répartition par gravité (3 parts, G11), jauge en anneau, matrices route × lumière et mode × âge, boîtes à moustaches (âges des tués par mode ; dispersion des départements par année), barres 100 % par année (lieu des tués ; mode des tués avec la palette catégorielle `cat-1…6`, autorisée quand une comparaison exige plusieurs couleurs).
- Carte : une seule grande carte avec bascule tués / victimes, projection conique conforme, classement des 10 premiers à côté (au lieu de deux cartes côte à côte).
- Boîtes « âge des tués » : statistiques nationales précalculées dans le pipeline (non additives, G15), donc non filtrables par département (puce « France métropolitaine »).
- Boîtes « dispersion des départements » : victimes pour 100 000 hab. (les tués par million seraient trop souvent masqués par le seuil, ce qui fausserait la distribution).
- Deuxième série demandée par le propriétaire : menu latéral repliable (≥ 1200 px, mémorisé dans le navigateur), KPI plus fins (196 px, filet fin, liseré ambre sur la vedette), jauges semi-circulaires (létalité vs 2019 ; gravité du mode vs ensemble), rose des mois (saisonnalité), radar de gravité par contexte, calendrier années × mois, graphique de pente 2019 → 2025.
- ECharts ajouté à la demande du propriétaire (accord G14, 01/11/2026) : ECharts 5.5.1 copié dans `app/assets/vendor/` (aucun paquet pip, fonctionne hors ligne). Utilisé pour les jauges (scènes 02 et 04), la rose des mois (02) et le radar (04) ; Plotly reste pour le reste (cartes, Sankey, matrices). Options construites en Python depuis les tokens (`app/echarts.py`), format français et `prefers-reduced-motion` appliqués côté client (`app/assets/echarts_route.js`) ; menu ⋯ (agrandir, PNG, données) compatible. Le test G9 exclut `assets/vendor/` (code tiers minifié).
- Remplissages semi-transparents calculés depuis les tokens (`tokens.transparence`), jamais de couleur en dur.

## Phase 5
- Filtres : bouton-résumé + panneau (années en sélecteur segmenté, recherche, raccourcis, réinitialisation) — plus lisible que deux petits menus, à la demande du propriétaire.
- Carte : fond en ligne (tuiles Carto Positron / Dark Matter via MapLibre, sans clé) par défaut + fond simple hors ligne — demande du propriétaire ; DESIGN §8 excluait les fonds tuilés.
- Analyses reprises des dépôts de référence (creps250 « Blood donation », Indabax) : Sankey, entonnoir, pyramide des âges, treemap ; non repris : nuages de mots (pas de texte libre), traduction anglaise (interface 100 % française), assistant IA, `pictorialBar` (ECharts), couleurs en dur, donuts > 3 parts, émojis.
- Palettes séquentielle et catégorielle rafraîchies (plus de contraste entre classes) — demande du propriétaire.
- Performances : caches (tables filtrées, carte de base, petits multiples) ; petits multiples construits en dictionnaire (make_subplots trop lent).

## Constats contraires aux hypothèses (G3)
- Scène 05, météo : la pluie est associée à **moins** d'accidents par département-jour (pluie faible RR 0,93, IC 0,93–0,94 ; pluie forte 0,92 ; gel 0,91), et « première pluie » n'a pas d'effet significatif (RR 1,01, IC 0,98–1,04). Le titre de la scène 05 ne dira donc pas que les premières pluies sont critiques.
- Scène 04 : la létalité des 2RM (4,0 tués / 100 victimes) est inférieure à celle des occupants de voiture (4,9) ; c'est sur le taux de gravité que les 2RM ressortent.
- Scène 05 : les cases les plus létales sont des nuits de semaine (mercredi 3 h sur le cumul), pas seulement de week-end ; le titre de la heatmap est désormais calculé (« Entre minuit et 6 h, une victime est X fois plus souvent tuée »).
- Scène 05 : le titre ne parle plus de « départements ruraux » (non calculé) mais de l'écart mesuré entre départements (de 1 à 7).

## Assistant de questions (RAG ancré)
- Demandé par le propriétaire (« agent IA du dashboard »). Choix : assistant **ancré sur les données, sans IA externe** (ni clé d'API, ni coût, hors ligne).
- Pourquoi pas un vrai LLM : G1 (aucun chiffre inventé) interdit qu'un modèle génère un nombre ; un LLM pourrait halluciner un chiffre faux dans une présentation au comité. Ici, **tout nombre vient d'une fiche calculée depuis les Parquet** ; le moteur ne fait que retrouver la bonne fiche.
- Technique : base de ~150 fiches construite au démarrage (`app/assistant.py`), récupération par TF-IDF + cosinus avec normalisation d'accents et dictionnaire de synonymes (morts→tués, moto→2RM, trottinette→EDP…). Aucune nouvelle dépendance (Python + pandas).
- Chaque réponse affiche aussi le **petit graphique** de la fiche (courbe annuelle, barres, palmarès),
  construit avec le thème courant et redessiné au changement clair/sombre.
- Garde-fous : source et lien vers la scène sous chaque réponse ; question hors sujet → message « aucune réponse dans les données » (jamais d'invention). Tests dans `tests/test_assistant.py`.

## Chute en euros, illustrations et couleurs (01/11/2026, décidé avec le propriétaire)
- **Valeurs tutélaires renseignées** : ce ne sont pas des chiffres inventés mais les valeurs OFFICIELLES de
  l'ONISR (méthode Quinet, « Le coût de l'insécurité routière », bilan 2021), vérifiées par recherche :
  tué 3 575 000 €, blessé hospitalisé 446 887 €, blessé léger 17 875 €. `verifie: false` : à confirmer par le
  propriétaire. Coût = victimes × valeurs (G1) ; 20,7 Md€ pour la métropole 2025.
- **Illustrations véhicules** : SVG isométriques générés (`design/vehicules.py`), couleurs lues dans
  `tokens.VEHICULE_PALETTE` (G9, aucun hexadécimal dans le générateur). Bande d'accueil informative
  (part de tués par mode), pas décorative.
- **Échelle séquentielle ambre** : auparavant elle finissait sur un rouge proche du rouge d'alerte, ce qui
  brouillait G10 (heatmap « valeur haute » vs « ce que le titre désigne »). Passée en ambre/bronze de la
  marque : le rouge d'alerte redevient unique et la marque entre dans les graphiques.

## Allègement du récit (01/11/2026)
- **Scène « Le paradoxe » dégraissée** : le donut « 68 % des tués hors agglomération » répétait à l'identique le KPI du haut (qui porte en plus la variation, la sparkline et le détail par route). Retiré ; la heatmap route × lumière passe en pleine largeur. Les autres graphiques portent chacun une information distincte et sont conservés.
- **Ponts narratifs** (`app/scenes.py` PONTS) : une phrase de liaison relie chaque scène à la suivante, au-dessus du bouton « suivant » (ex. « On sait où le risque est le plus grave. Reste à savoir qui le subit. »). Tension entretenue d'une scène à l'autre.
- **Bouton flottant de l'assistant** : dégagé du bas de scène (marge) pour ne plus chevaucher le bouton « Scène suivante » (défaut d'accessibilité corrigé).

## Trois chantiers + audit (02/11/2026)
- **Simulateur premium** : illustration isométrique du véhicule du profil choisi (callback clientside, 9 types couverts — ajout utilitaire / bus / EDP / autre) + badge-verdict qualitatif (couleur **et** texte, G12). Scène dédiée `.sim-scene`, tokens uniquement (G9/G10).
- **Authentification** : garde Flask (session signée) avant le tableau de bord ; page de connexion premium (couleurs issues des tokens, G9). Identifiants de démonstration `actuaire` / `risque2026`, surchargeables par `APP_UTILISATEUR` / `APP_MOTDEPASSE` / `APP_SECRET` ; `APP_AUTH=0` désactive la garde (QA/dev). Anti-redirection ouverte sur `?next`.
- **Bilingue FR/EN** : `app/i18n.py` (langue via cookie, lue à chaque requête) ; `app.layout` en fonction (`serve_layout`) + bascule FR/EN dans l'en-tête (recharge). **Traduit** : tout le cadre (en-tête, navbar, filtres, boutons, ponts, assistant-coquille, menu et pied des graphiques, modale « Données ») + **simulateur** 100 % (libellés, options à valeur conservée, titre/chapeau/encart, phrase et nombres JS, badge) + page de connexion.
  - **Non traduit (choix G3)** : les titres-messages analytiques des scènes 02–06 sont générés depuis les données ; leur version anglaise doit être validée par le propriétaire (un titre ne doit pas mentir). Les réponses de l'assistant restent en français (corpus de données français). Extension triviale : ajouter les clés dans `app/i18n.py`.
- **Audit** : `pytest` vert (54), `ruff` propre, `qa_filtres` sans erreur de callback (8 pages × filtres). En-tête mobile < 480 px sans débordement. Texte alt du véhicule localisé.
- **À décider avec le propriétaire** : (1) latence du changement de filtre (~1 s, rechargement complet) → servir en production (waitress) demanderait une dépendance (G14) ; (2) traduction EN des corps analytiques des scènes 02–06.
