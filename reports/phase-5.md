# Phase 5 — Finitions et contrôle qualité

## Fait
- Performances : tables filtrées mises en cache (`data_access.filtre_table`), matrice mode × âge vectorisée,
  carte de base mise en cache (seul le contour du département filtré est ajouté), petits multiples construits
  directement en dictionnaire. Calcul des callbacks : 20 à 270 ms (mesure directe, sans file du serveur de dev).
- Filtres refondus : bouton-résumé « période · territoire » dans l'en-tête, panneau avec années en sélecteur
  segmenté, recherche de département, raccourcis (France métropolitaine, département le plus touché),
  réinitialisation ; synchronisés avec l'URL et la session.
- Carte : deux fonds au choix, « Fond en ligne » (tuiles Carto via MapLibre, clair / sombre, sans clé) et
  « Fond simple » (hors ligne).
- Nouvelles analyses inspirées des dépôts de référence : Sankey mode → lieu → gravité, entonnoir de gravité,
  pyramide des âges des tués (par million d'habitants), treemap mode × route (surface = tués, couleur =
  létalité) ; plus jauges, rose des mois, radar, calendrier, pente (phase 4).
- Palettes séquentielle et catégorielle rafraîchies (tokens + CSS, tests de cohérence).
- Accessibilité : `lang="fr"`, double anneau de focus sur la carte vedette, trous (et non zéros) dans le
  radar sous le seuil.
- `README.md`, `reports/SYNTHESE.md`, captures finales `reports/screens/final/` (8 scènes × clair / sombre ×
  1440 / 1024 / 390).

## Relecture finale indépendante : défauts corrigés
- Variations de la courbe de létalité calculées sur des valeurs arrondies → valeurs exactes, en points.
- Encarts nationaux sans période à côté de chiffres de l'année filtrée → « Sur 2019–2025 » / années citées.
- Rose des mois : comparaison sur des mois sous 30 tués (G6) → titre neutre sauf si chaque mois ≥ 30.
- Calendrier illisible à 390 px → version mobile sans texte dans les cases.
- `<html lang="">` → `lang="fr"`.
- Mineurs : titre de la scène 04 (« sont les plus exposés »), radar, focus de la vedette, valeur « pluie
  forte 0,92 » dans DECISIONS.

## Checklist §8 (CLAUDE.md)
- [x] Aucun chiffre en dur, aucun texte de remplissage dans l'interface (G1) — titres, KPI, encarts et titres
      de graphiques calculés ; 22 chiffres recalculés par la relecture finale, écarts corrigés.
- [x] Chaque titre-message reflète les données (G3) — constats contraires consignés dans DECISIONS.
- [x] Taux rapportés à une exposition, seuil d'effectif appliqué (G5, G6) — `masque_seuil`, tests
      `test_aucun_taux_sous_le_seuil`, cumul pour les taux départementaux.
- [x] Zéro hexadécimal hors `tokens.py` / `custom.css` (G9) — test automatisé (hexadécimaux 3/4/6/8 chiffres,
      rgb/rgba/hsl) ; l'illustration SVG du héros est générée depuis les tokens.
- [x] Une seule couleur d'alerte par graphique (G10) — gravité (tués / hospitalisés / légers) et palette
      catégorielle utilisées seulement quand la comparaison l'exige (DECISIONS).
- [x] Mode clair et sombre corrects, y compris les figures Plotly — templates par mode, re-rendu au
      changement de thème, captures `*_dark_*`.
- [x] Navigation clavier complète, focus visible, contrastes AA — Tab sur filtres, thème, navbar, KPI
      (Entrée retourne), menus ⋯ ; anneau `--focus-ring` ; contrastes recalculés (≥ 4,5:1 pour le texte).
- [x] Rendu vérifié à 1440, 1024 et 390 px — captures finales et contrôle automatique des débordements KPI.
- [x] Premier affichage < 2 s — 0,8 à 1,6 s (accueil 1,6 s) en local.
- [~] Changement de filtre < 300 ms — calcul de chaque callback 20–270 ms ; en serveur de développement, les
      5 à 8 callbacks d'une scène passent en file (0,3 à 0,9 s perçus). Un serveur de production multi-
      processus est recommandé (README, SYNTHESE).
- [x] Aucune erreur dans la console du navigateur ni dans le terminal — seuls des avertissements de
      performance du pilote WebGL (fond de carte en ligne) en navigateur sans écran.
- [x] Sources et définitions sous chaque graphique.
- [x] `pytest` vert (50 tests), `ruff` propre.

## Défauts mineurs restants
- Changement de filtre perçu au-delà de 300 ms en serveur de développement (voir ci-dessus).
- Boîtes « âge des tués » nationales (statistiques non additives).
- Captures pleine page : la navbar fixe s'arrête à la hauteur de la fenêtre (artefact de capture).
- Le fond de carte en ligne demande une connexion (le fond simple reste disponible hors ligne).
