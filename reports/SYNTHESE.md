# Synthèse — « Risque routier »

## Ce qui a été construit
- **Pipeline de données** (`pipeline/`) : lecture des BAAC 2019–2025 avec 14 corrections (dont 2 pièges
  absents du LISEZMOI), table usager enrichie (871 534 usagers), 23 agrégats Parquet, 2 modèles (GLM
  météo quasi-Poisson, régression logistique du simulateur), contrôles de cohérence G4.
- **Design system « Route de nuit »** (`design/`, `app/assets/custom.css`) : tokens uniques, thème
  Mantine, templates Plotly clair et sombre, illustration du héros générée, contrastes AA vérifiés.
- **Application Dash + DMC 2.8.1** (`app/`) : 8 scènes, filtres période / territoire synchronisés avec
  l'URL (bouton-résumé + panneau), mode clair / sombre, menu latéral repliable, cartes KPI retournables,
  plus de trente graphiques (courbes annotées, anneaux, jauges, matrices, boîtes à moustaches, radar, rose
  des mois, Sankey, entonnoir, pyramide des âges, treemap, carte sur fond en ligne ou simple + classement,
  calendrier, pente, Pareto, petits multiples), simulateur calculé dans le navigateur, table exportable.
- **Assistant « RAG ancré »** (`app/assistant.py`) : zone de questions en langage naturel ; les
  réponses sont des fiches calculées depuis les Parquet (aucun chiffre généré par un modèle, G1),
  récupérées par recherche lexicale TF-IDF hors ligne, **avec le graphique correspondant**, leur
  source et un lien vers la scène.
- **Qualité** : 54 tests (contrats de données, formules, seuil G6, G9, formats), ruff propre, QA
  playwright (filtres, captures, performances), 5 relectures indépendantes corrigées.

## Les 8 scènes et leur titre-message final (généré depuis les données)
| # | Scène | Titre-message |
| --- | --- | --- |
| 01 | Accueil | 3 263 personnes tuées sur la route en 2025, soit 8,9 par jour |
| 02 | Vue d'ensemble | Les tués ne baissent plus : *2025 retrouve le niveau de 2019.* |
| 03 | Le paradoxe | La ville fait les accidents, *la campagne fait les morts.* |
| 04 | Qui | Les jeunes hommes et les deux-roues *sont les plus exposés aux blessures graves.* |
| 05 | Où et quand | Selon le département, le risque de mourir sur la route *varie de 1 à 7.* |
| 06 | Ce qui change | Les victimes en trottinette ou EDP *ont été multipliées par 5 depuis 2019.* |
| 07 | Simulateur | Le mode de déplacement et le lieu *pèsent plus que la nuit ou la pluie.* |
| 08 | Méthode et données | Chaque chiffre vient des données, *et se vérifie.* |

## Chiffres clés (France métropolitaine)
- **3 263 tués en 2025** (3 244 en 2019, 2 541 en 2020) ; 18 345 blessés hospitalisés ; 68 629 victimes.
- Victimes **−7 %** depuis 2019, tués **+0,6 %** : la létalité passe de **4,4 à 4,8** tués pour 100 victimes.
- **64 %** des accidents en agglomération, **68 %** des tués hors agglomération ; hors agglomération, une
  victime est **3,0 fois** plus souvent tuée. Départementales : 38 % des accidents, **61 % des tués**.
- Pic de blessures graves chez les **hommes de 20–24 ans** : 110 pour 100 000 habitants et par an,
  **3,1 fois** les femmes du même âge. Hommes : 3,7 fois plus de tués par habitant que les femmes.
- **2RM** : 22 % des tués ; une victime en 2RM est tuée ou hospitalisée dans **38 %** des cas (voiture 28 %).
  **51 %** des piétons tués ont 65 ans ou plus.
- Départements (cumul 2019–2025) : de **14 tués par million** d'habitants (Hauts-de-Seine) à **101**
  (Alpes-de-Haute-Provence).
- Nuits de week-end : **7,3** tués pour 100 victimes, contre 4,6 en moyenne.
- Météo (GLM) : les jours de pluie comptent **moins** d'accidents (risque relatif 0,93) ; la « première
  pluie » après 7 jours secs n'a **pas d'effet significatif** (1,01, IC 0,98–1,04).
- **EDP** (trottinettes) : victimes ×5 (677 → 3 409) ; vélo +16 % ; voiture −8 %.
- **5 segments sur 18** (mode × agglomération) concentrent 84 % des tués et hospitalisés.

## Écarts au brief et pourquoi (détail dans `reports/DECISIONS.md`)
- **Météo (scène 05)** : l'hypothèse « premières pluies critiques » est contredite par les données ; le
  titre et l'encart disent le constat réel (G3).
- **Matrice de la scène 04** : axe Y = taux de gravité au lieu de la létalité (en létalité, les 2RM passent
  sous la voiture ; le constat est sur la gravité).
- **Taux départementaux** calculés sur le cumul 2019–2025 : par an, le seuil G6 masquait la moitié des
  départements, ruraux surtout.
- **Simulateur** : risque relatif (probabilité / moyenne observée) plutôt qu'un rapport de cotes présenté
  comme un risque.
- **Contrastes** : `text-muted` et le rouge du mode sombre éclaircis pour respecter l'AA (G12 prime sur
  DESIGN §2.1).
- **Cartes KPI épurées** à votre demande (une variation, ligne leader au verso, source en infobulle) :
  écart assumé à DESIGN §6.2 et §12.
- **ECharts** ajouté avec votre accord (jauges, rose des mois, radar ; local, sans pip) ; reprise des bonnes idées
  des deux dépôts de référence (Sankey, entonnoir, pyramide, treemap, jauges, rose, radar).
- **Fond de carte en ligne** (tuiles Carto) ajouté à votre demande, en plus du fond simple hors ligne (DESIGN
  §8 excluait les fonds tuilés).

## Ce qu'il vous reste à faire
1. **Renseigner `config/references.yaml`** avec leur source : valeurs tutélaires du coût d'un tué, d'un
   blessé hospitalisé, d'un blessé léger (bilan ONISR de l'année de référence), et part des 2RM dans le
   trafic. Tant qu'elles valent `null`, l'application affiche « À renseigner » et le Pareto pondère par
   tués + hospitalisés.
2. **Comparer `reports/controles.md` aux bilans ONISR** de chaque année (accidents, victimes, tués,
   métropole et France entière). Écart connu : le brief annonçait 58 841 accidents en 2019 et 47 745 en
   2020 ; le calcul donne 58 840 et 47 744.
3. **Valider les décisions** de `reports/DECISIONS.md`, en particulier les écarts au design system.
4. Étendre ECharts à d'autres graphiques si le rendu vous plaît.
5. Remplacer, si vous le souhaitez, l'illustration générée du héros par une photo libre de droits.

## Améliorations possibles
- Mettre l'application derrière un serveur de production (gunicorn / waitress) et un cache partagé
  (`flask-caching`) : les callbacks font 20 à 270 ms de calcul, mais le serveur de développement les
  exécute en file.
- Exposition au trafic (kilomètres parcourus) pour remplacer la population quand elle sera disponible.
- Rendre filtrables par département les statistiques non additives (boîtes d'âge) en les précalculant
  par département.
- Coût socio-économique par segment dès que les valeurs tutélaires sont renseignées.
- Version Quarto du concours à partir des mêmes `pipeline/` et `design/`.
