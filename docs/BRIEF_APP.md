# BRIEF_APP.md — Contenu de l'application « Risque routier »

> Le **quoi** : données, préparation, indicateurs, 8 scènes, KPI, graphiques, cartes, simulateur, textes.
> La forme visuelle est dans `DESIGN_SYSTEM.md`. Les garde-fous G1–G18 de `CLAUDE.md` s'appliquent partout.

---

## 1. Données disponibles (lecture seule)

| Source | Chemin | Grain | Notes |
| --- | --- | --- | --- |
| BAAC caractéristiques | `data/baac/<an>/caract-<an>.csv` | 1 ligne / accident | `;`, UTF-8, `lat`/`long` décimale virgule |
| BAAC lieux | `data/baac/<an>/lieux-<an>.csv` | ≥ 1 ligne / accident | **doublons de `Num_Acc`** |
| BAAC véhicules | `data/baac/<an>/vehicules-<an>.csv` | 1 ligne / véhicule | 2025 : en-tête cassé |
| BAAC usagers | `data/baac/<an>/usagers-<an>.csv` | 1 ligne / usager impliqué | 2019–2020 sans `id_usager` |
| Météo département-jour | `data/meteo/meteo_dep_jour_2019_2025.csv` | dép. × jour | colonnes ci-dessous ; Corse = `20` |
| Météo stations | `data/meteo/meteo_stations_2019_2025_part*.csv.gz` | station × jour | **ne pas charger dans l'app** (6,4 M lignes) |
| Population INSEE | `data/insee/insee_estim-pop-dep-sexe-aq-1975-2026.xlsx` | dép. × sexe × âge quinquennal × année | un onglet par année |
| Parc SDES | `data/sdes/sdes_parc_vehicules_dep_2019_2026.csv` | dép. × carburant × statut × groupe × catégorie | **pas de 2RM** ; `dep=00` à exclure |
| Contours | `data/geo/departements-version-simplifiee.geojson` | 96 dép. métropole | clé `properties.code` (01…95, 2A, 2B) |

Années : **2019 à 2025** (format homogène depuis 2019). Accidents par an : 47 745 (2020) à 58 841 (2019).

**Météo, colonnes** : `dep;date;rr_moy_mm;part_stations_pluie_1mm;tn_moy;tn_min;tx_moy;part_stations_gel;fxi_max_ms;n_stations_rr`
(pluie moyenne des stations en mm, part des stations avec ≥ 1 mm, températures min/max moyennes en °C, part des stations
avec TN ≤ 0 °C, rafale max en m/s, nombre de stations).

**INSEE, structure d'un onglet** : lignes 1–5 = en-têtes ; ligne 4 = blocs « Ensemble », « Hommes », « Femmes » ;
ligne 5 = classes `0 à 4 ans` … `95 ans et plus`, `Total` (21 colonnes par bloc) ; données à partir de la ligne 6 :
col. A = code département, col. B = nom. Des lignes d'agrégat existent (`France métropolitaine`, `DOM`,
`France métropolitaine et DOM`) et des codes DOM sont des **entiers** (971…) → normaliser en texte et exclure les agrégats.
Contrôle : somme des classes = `Total` pour chaque ligne.

## 2. Préparation (pipeline/)

### 2.1 Corrections obligatoires à la lecture
1. Lire tous les CSV BAAC en `dtype=str`, `sep=";"`, puis convertir explicitement.
2. **2022** : `caract-2022.csv` nomme la clé `Accident_Id` → renommer `Num_Acc`.
3. **2019–2020** : `usagers` n'a pas `id_usager` → créer un identifiant (`Num_Acc` + rang).
4. **2025** : dans `vehicules-2025.csv`, le nom de colonne `"id_vehicule"` contient un retour à la ligne (entre guillemets),
   l'en-tête s'étale donc sur deux lignes physiques. Un lecteur CSV qui respecte les guillemets le lit correctement :
   nettoyer alors les noms (`df.columns = df.columns.str.strip()`). Sinon, imposer les noms
   `Num_Acc;id_vehicule;num_veh;senc;catv;obs;obsm;choc;manv;motor;occutc`. Dans les deux cas, vérifier 11 colonnes et
   l'égalité des colonnes avec 2024.
5. **2019** : `dep` sans zéro initial (`1` au lieu de `01`) → `zfill(2)` sauf `2A`, `2B` et codes à 3 caractères.
6. `lat`, `long` : remplacer `,` par `.` puis `float`.
7. Valeurs `-1` (et `0` quand le PDF dit « non renseigné ») → manquant.
8. `id_vehicule` contient des espaces (`"155 680 557"`) → garder en texte, ne pas convertir en nombre.
9. **`lieux`** : plusieurs lignes par `Num_Acc` → garder **une** ligne par accident (la première). Tester l'unicité.
10. **Usagers en fuite (depuis 2021, avertissement ONISR)** : sexe, âge et parfois gravité manquants → exclus des
    calculs qui demandent la variable manquante, comptés ailleurs ; leur nombre par an va dans `reports/controles.md`.
11. `vma` : garder seulement {10, 20, 30, 40, 50, 60, 70, 80, 90, 110, 130} ; le reste → manquant.
12. `catv` : normaliser en entier (`"07"` et `"7"` → 7).

### 2.2 Codes (vérifiés dans le PDF officiel le 01/11/2026 — revérifier en cas de doute, G2)

- `grav` : 1 indemne · 2 tué (décès dans les 30 jours) · 3 blessé hospitalisé (> 24 h) · 4 blessé léger
- `catu` : 1 conducteur · 2 passager · 3 piéton
- `sexe` : 1 masculin · 2 féminin
- `agg` : 1 hors agglomération · 2 en agglomération
- `lum` : 1 plein jour · 2 crépuscule ou aube · 3 nuit sans éclairage · 4 nuit éclairage non allumé · 5 nuit éclairage allumé
- `atm` : 1 normale · 2 pluie légère · 3 pluie forte · 4 neige-grêle · 5 brouillard · 6 vent fort · 7 éblouissant · 8 couvert · 9 autre
- `catr` : 1 autoroute · 2 nationale · 3 départementale · 4 voie communale · 5 hors réseau public · 6 parking · 7 route de métropole urbaine · 9 autre
- `surf` : 1 normale · 2 mouillée · 3 flaques · 4 inondée · 5 enneigée · 6 boue · 7 verglacée · 8 corps gras · 9 autre
- `col` : 1 frontale · 2 par l'arrière · 3 par le côté · 4 en chaîne (3+) · 5 multiples (3+) · 6 autre · 7 sans collision
- `obs` (obstacle fixe) : 0 sans objet · 2 arbre · 13 fossé/talus · 16 sortie de chaussée sans obstacle · (liste complète dans le PDF)
- `secu1-3` : 0 aucun · 1 ceinture · 2 casque · 3 dispositif enfants · 4 gilet · 5 airbag 2RM · 6 gants · 7 gants + airbag · 8 non déterminable · 9 autre

### 2.3 Variables dérivées
- `victime` = `grav ∈ {2,3,4}` ; `grave` = `grav ∈ {2,3}` ; `tue` = `grav == 2`.
- `age` = `an − an_nais` (gardé si 0 ≤ âge ≤ 110) ; `classe_age` alignée sur l'INSEE (`0-4`, `5-9`, …, `95+`).
- `date` = `an-mois-jour` ; `jour_semaine` ; `heure` = heure de `hrmn` ; `weekend` ; `nuit` = `lum ∈ {3,4,5}`.
- `type_usager` (piéton d'abord, sinon d'après le `catv` du véhicule de l'usager) :

| `type_usager` | Règle |
| --- | --- |
| Piéton | `catu == 3` |
| Vélo | `catv ∈ {1, 80}` (bicyclette, VAE) |
| EDP | `catv ∈ {50, 60}` (trottinettes et engins de déplacement personnel) |
| 2RM | `catv ∈ {2, 30, 31, 32, 33, 34, 41, 42, 43}` (cyclos, scooters, motos, 3RM) |
| Voiture | `catv ∈ {3, 7}` |
| Utilitaire | `catv == 10` |
| Poids lourd | `catv ∈ {13, 14, 15, 16, 17}` |
| Bus, car, tram | `catv ∈ {37, 38, 39, 40}` |
| Autre | tout le reste (quads, engins, tracteurs agricoles, 0, 99) |

- Périmètre géographique : `metropole` = `dep` ∉ {971, 972, 973, 974, 975, 976, 977, 978, 986, 987, 988}.
  **Cartes et taux : métropole uniquement.** Les DOM n'apparaissent que dans la page Données.

### 2.4 Table pivot et agrégats (`data/processed/`)
- `usagers_enrichis.parquet` : 1 ligne par usager, avec les colonnes utiles de `caract`, `lieux`, `vehicules` et les
  variables dérivées. Jointures : `usagers ⟷ vehicules` sur (`Num_Acc`, `id_vehicule`), puis ⟷ `caract` et `lieux`
  sur `Num_Acc`.
- `accidents.parquet` : 1 ligne par accident (`caract` + `lieux` dédoublonné + nombre de tués / graves / victimes).
- `expo_population.parquet` : dép. × année × sexe × classe d'âge → population (métropole, 2019–2025).
- `expo_parc.parquet` : dép. × année × groupe (VP, VUL, PL, TCP) → parc au 1er janvier.
- `meteo_dep_jour.parquet` : la météo, avec Corse dupliquée en `2A` et `2B`, et une variable `meteo_cat` :
  `sec` (rr_moy < 0,2 mm), `pluie faible` (0,2–5 mm), `pluie forte` (≥ 5 mm), `gel` (part_stations_gel ≥ 0,5),
  plus `premiere_pluie` = 1er jour de pluie (≥ 1 mm) après ≥ 7 jours secs consécutifs dans le département.
- Un Parquet d'agrégats **par scène** (`s02_*.parquet`, `s03_*.parquet`…), au grain le plus fin dont les filtres ont
  besoin (année × département au minimum), pour que les callbacks ne fassent que filtrer et sommer.
- `models/*.json` : coefficients des GLM (§5 et scène 07).

## 3. Indicateurs (définitions uniques, dans `pipeline/indicators.py`)

| Indicateur | Formule | Affichage |
| --- | --- | --- |
| Accidents | nombre de `Num_Acc` | entier |
| Victimes | usagers `grav ∈ {2,3,4}` | entier |
| Tués / hospitalisés / légers | usagers par `grav` | entier |
| Létalité | tués / victimes × 100 | « X,X tués pour 100 victimes » |
| Taux de gravité | (tués + hospitalisés) / victimes | % |
| Victimes pour 100 000 hab. | victimes / population × 100 000 | 1 décimale |
| Tués par million d'hab. | tués / population × 1 000 000 | 1 décimale |
| Accidents pour 10 000 véhicules | accidents impliquant le groupe / parc du groupe × 10 000 | 1 décimale |
| Base 100 | valeur année N / valeur 2019 × 100 | entier |
| Risque relatif | exp(coefficient GLM), IC 95 % | « × 1,32 » |

Rappel G6 : sous 30 victimes au dénominateur concerné, le taux n'est pas affiché.
Mention à afficher dans la méthode : l'indicateur « blessé hospitalisé » n'est plus labellisé par la statistique publique
depuis 2019 (avertissement ONISR) ; il reste utilisable pour des comparaisons internes à la période.

## 4. Filtres globaux (header)

- **Période** : `2019–2025` (cumul) ou une année. Défaut : dernière année (2025) pour les KPI, toute la période pour les
  courbes d'évolution (les scènes d'évolution ignorent le filtre d'année et l'indiquent par une puce « Toutes années »).
- **Territoire** : France métropolitaine (défaut) ou un département (recherche par nom ou code).
- L'état des filtres est conservé dans `dcc.Store` (session) et reflété dans l'URL (`?annee=2025&dep=29`).
- Toute carte graphique filtrée affiche une puce de filtre actif.

## 5. Les 8 scènes

Chaque scène = **en-tête** (numéro, nom, titre-message, chapeau) → **rangée de KPI** → **1 ou 2 cartes graphiques** →
**encart « Et alors ? »** → **navigation**. Les titres entre « » sont des hypothèses : les formuler depuis les données (G3).
Les `X` sont des valeurs calculées. Chaque KPI est une **carte retournable** (DESIGN §6.2) : recto = valeur, verso =
« Comment le lire » + lecture assureur + source.

### Scène 01 — Accueil (`/`)
- **Carte héros** plein écran : image de route de nuit sous la pluie (sobre, sans accident ni personne identifiable),
  sur-titre « Sécurité routière · France métropolitaine · 2019–2025 », chiffre géant = tués de la dernière année,
  phrase « soit X par jour » (tués / 365, 1 décimale) apparaissant après 1 s, bouton « Commencer » → scène 02.
- Sous le héros : triptyque « Fréquence · Gravité · Coût » en trois mots-clés avec une ligne chacun.
- Pas de graphique.

### Scène 02 — Vue d'ensemble (`/vue-ensemble`)
- **Question** : quelle est l'ampleur du risque et comment évolue-t-il ?
- **Titre-hypothèse** : « Le nombre de tués ne baisse plus depuis la sortie du COVID. »
- **KPI (4)** :
  1. Tués (année filtrée) — ▲▼ vs N−1 et vs 2019 — ligne leader : type d'usager qui pèse le plus parmi les tués (X %).
  2. Blessés hospitalisés — ▲▼ vs N−1 et vs 2019 — leader : type d'usager.
  3. Létalité (tués / 100 victimes) — ▲▼ — leader : catégorie de route la plus létale.
  4. Victimes pour 100 000 hab. — ▲▼ — leader : département au taux le plus élevé.
  Chaque KPI a une mini-courbe 2019–2025 (neutre, dernier point rouge).
- **Graphique 1** : courbe **base 100 (2019)** des tués, hospitalisés et légers ; tués en rouge, les deux autres en
  neutre ; bande grise sur 2020 annotée « Confinements » ; dernier point étiqueté.
- **Graphique 2** : barres verticales des **tués par an** (valeur au-dessus de chaque barre), dernière année en rouge.
- **Et alors ?** : la tendance des tués et ce qu'elle implique pour l'hypothèse de dérive de la sinistralité corporelle.

### Scène 03 — Le paradoxe (`/paradoxe`)
- **Question** : les accidents et les tués sont-ils au même endroit ?
- **Titre-hypothèse** : « La ville fait les accidents, *la campagne fait les morts*. »
- **KPI (4)** : part des accidents en agglomération · part des tués hors agglomération · létalité hors agglomération ·
  ratio de létalité hors / en agglomération (« × X »).
- **Graphique 1 — barres miroir** par catégorie de route (`catr` : autoroute, nationale, départementale, communale,
  métropole urbaine ; le reste regroupé) : à gauche **part des accidents**, à droite **part des tués**, même échelle
  0–100 %. La catégorie où l'écart est maximal est en rouge et annotée.
- **Graphique 2 — létalité par vitesse maximale autorisée** (`vma` 30 → 130) : barres, rouge pour la classe la plus
  létale, ligne de référence = létalité moyenne. Bascule `SegmentedControl` : « Vitesse autorisée » / « Lumière »
  (`lum` regroupé : jour, aube-crépuscule, nuit éclairée, nuit non éclairée) / « Obstacle heurté » (arbre, fossé, aucun…).
- **Et alors ?** : en zone rurale c'est la sévérité, pas la fréquence, qui pilote le coût corporel.

### Scène 04 — Qui (`/qui`)
- **Question** : quels profils cumulent fréquence et gravité ?
- **Titre-hypothèse** : « Jeunes adultes, seniors et deux-roues concentrent la gravité. »
- **KPI (4)** : classe d'âge au taux de victimes graves le plus élevé (pour 100 000 hab.) · ratio hommes / femmes des
  tués par habitant · part des 2RM parmi les tués · part des piétons de 65 ans et plus parmi les piétons tués.
- **Graphique 1 — risque par âge** : deux courbes (hommes, femmes) des **victimes graves pour 100 000 habitants** par
  classe quinquennale ; pic annoté ; hommes en rouge si l'écart est le message, sinon neutre foncé / neutre clair.
- **Graphique 2 — matrice fréquence × gravité** (nuage à bulles) : un point par `type_usager` ; x = part des victimes,
  y = létalité ; taille = nombre de tués ; quadrants nommés (« fréquent et bénin », « rare et mortel »…) ; 2RM (ou le
  type qui ressort) en rouge, le reste neutre ; étiquettes directes, pas de légende.
- **Option** (si le temps le permet) : létalité des usagers de 2RM selon le port du casque (`secu1-3` contient 2) —
  uniquement si l'effectif sans casque dépasse le seuil.
- **Et alors ?** : quelles variables de tarification (âge, type de véhicule) captent vraiment la gravité.

### Scène 05 — Où et quand (`/ou-quand`)
- **Question** : quels territoires et quels moments sont les plus risqués ?
- **Titre-hypothèse** : « Les départements ruraux ont moins d'accidents mais plus de morts ; nuits de week-end et premières
  pluies sont critiques. »
- **KPI (4)** : département au taux de tués par million d'hab. le plus élevé · le plus faible · créneau jour × heure le plus
  létal · risque relatif « première pluie » (× X).
- **Graphique 1 — deux cartes choroplèthes côte à côte** (métropole) : à gauche **victimes pour 100 000 hab.**, à droite
  **tués par million d'hab.** ; 5 classes par quantiles (`seq-1`…`seq-5`) ; survol = nom, valeur, rang ; clic = filtre le
  département (puce « Filtre : <nom> ✕ ») ; légende en bas avec les bornes des classes.
- **Graphique 2 — heatmap** jour de la semaine (lignes, lundi → dimanche) × heure (colonnes 0–23) ; bascule
  « Accidents » / « Létalité » ; échelle `seq-*` ; cellules sous le seuil grisées ; nuits de week-end encadrées.
- **Graphique 3 — effet météo** : barres horizontales de **risque relatif** par `meteo_cat` (sec = référence × 1) avec
  moustaches IC 95 %, ligne verticale à × 1. Modèle : GLM Poisson sur `nb_accidents` par département-jour
  ~ `meteo_cat` + `dep` + `mois` + `annee` + `jour_semaine` (effets fixes), coefficients exponentiés.
- **Et alors ?** : la météo et l'heure sont des facteurs de risque mesurables, utiles pour la prévention ciblée et les
  offres « usage » (assurance au kilomètre, alertes).

### Scène 06 — Ce qui change (`/evolution`)
- **Question** : qu'est-ce qui dérive depuis 2019 ?
- **Titre-hypothèse** : « Les nouveaux usages (EDP, vélo) progressent pendant que la voiture recule. »
- **KPI (4)** : évolution des tués 2019 → dernière année (%) · évolution des victimes EDP · évolution des victimes vélo ·
  part des 2RM parmi les tués (dernière année).
- **Graphique 1 — petits multiples** : une mini-courbe base 100 par `type_usager` (même échelle Y, grille 3 × 3) ; le type
  qui progresse le plus en rouge, les autres neutres ; 2020 grisé.
- **Graphique 2 — Pareto** : barres des segments (`type_usager` × `agg`) triées par poids décroissant + courbe cumulée,
  seuil 80 % marqué. Poids = **coût socio-économique** si `config/references.yaml` contient les valeurs tutélaires
  sourcées (G8), sinon **tués + hospitalisés** (et le titre le dit).
- **Et alors ?** : quelques segments concentrent l'essentiel de la gravité : c'est là que tarification fine et prévention
  rapportent le plus ; veille sur les EDP.

### Scène 07 — Simulateur (`/simulateur`)
- **Question** : quel est le risque relatif d'un profil donné ?
- **Modèle** : régression logistique P(blessure grave | usager impliqué) = `grave` ~ `type_usager` + `classe_age` +
  `sexe` + `agg` + `nuit` + `meteo_cat` + `catr` (sur `usagers_enrichis`, métropole, 2019–2025). Coefficients et
  moyenne de référence exportés dans `models/simulateur.json`.
- **Interface** : colonne gauche = profil (`SegmentedControl` type d'usager ; `Slider` âge par classes ; `SegmentedControl`
  sexe ; `Switch` nuit, pluie, hors agglomération ; `Select` type de route). Colonne droite = jauge du **rapport de cotes
  vs profil moyen** (× X), probabilité estimée d'une blessure grave si impliqué (%), phrase générée (« Un motard de 20–24 ans,
  la nuit, sous la pluie, hors agglomération : risque de blessure grave × X par rapport au profil moyen »).
- Calcul **côté client** (`clientside_callback`) à partir du JSON : réponse instantanée.
- Bouton « Comparer » : superpose le profil moyen et le profil choisi.
- Mention fixe : « Estimation statistique sur 2019–2025, pas une prédiction individuelle. »

### Scène 08 — Méthode et données (`/methode`)
- Sources (avec liens), définitions (§3), corrections appliquées (§2.1), limites :
  pas de données d'assurance (coût socio-économique ≠ coût assureur) ; accidents corporels constatés par les forces de
  l'ordre uniquement ; blessés légers sous-déclarés ; exposition approchée (population, parc) faute de kilomètres
  parcourus ; pas de parc 2RM par département ; météo moyennée par département ; corrélation, pas causalité ;
  2020 atypique ; indicateur « hospitalisé » non labellisé depuis 2019 ; usagers en fuite depuis 2021.
- **Onglet Données** : `dash-ag-grid` des indicateurs par département × année (tri, filtre, export CSV), définitions au survol
  des en-têtes.

## 6. Textes

- Ton : grave, clair, sans jargon ; on parle de vies.
- Titre-message = conclusion, ≤ 12 mots ; chapeau = 1 phrase ; « Et alors ? » = 2 lignes maximum, toujours du point de vue
  de l'assureur.
- Sous chaque graphique : « Source : … » + définition de la mesure.
- Libellés en clair (« Hors agglomération », pas « agg=1 »).
