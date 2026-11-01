# Phase 3 — Composants isolés

## Fait
- `app/components/format.py` : `fmt_number`, `fmt_pct`, `fmt_ratio`, `delta` (flèche + couleur selon le sens
  pour l'assureur), espace fine insécable, signe moins typographique, « — » si manquant.
- `kpi_card.py` : carte retournable (recto : libellé + icône, valeur, ▲▼ vs N−1 et vs 2019, ligne leader,
  mini-courbe neutre au dernier point rouge, indice ; verso : comment le lire, pour l'assureur, source).
- `chart_card.py` : carte graphique (titre h2, sous-titre, puces de filtre, bascule, graphique, menu ⋯
  agrandir / PNG / données, pied source + définition), message « effectif trop faible ».
- `blocks.py` : en-tête de scène (moitié du titre en italique rouge), encart « Et alors ? », héros,
  triptyque, navigation précédente / suivante (liens-boutons), bascule responsive, gabarit de scène.
- `shell.py` : header (monogramme, triptyque, compteur de scène, filet de progression ambre, filtres
  Période / Territoire libellés avec icône, interrupteur de thème), navbar (badge, 8 liens numérotés),
  AppShell responsive (240 px ≥ 1200, icônes 768–1199, burger < 768).
- `app/callbacks_globaux.py` : modales Agrandir et Données, export PNG, synchronisation des bascules.
- `app/assets/app.js` : retournement au toucher et au clavier (aria-pressed), comptage animé au premier
  affichage, export PNG sur fond opaque.
- `design/hero.py` → `app/assets/hero-route-nuit.svg` : illustration générée (route de nuit sous la pluie,
  cinémagraphe de pluie désactivé en mouvement réduit).
- `sandbox/components_demo.py` : tous les composants avec données marquées « factices » (`/` héros,
  `/paradoxe` scène type).

## Vérifications
| Vérification | Résultat |
| --- | --- |
| `pytest -q` | 46 passés |
| `ruff check .` | propre |
| Démo sans erreur de callback / console | « aucune erreur » (reports/screens/phase-3/console.txt) |
| Hexadécimaux hors fichiers autorisés | 0 |
| Captures clair / sombre × 1440 / 390 | reports/screens/phase-3/{heros,scene}_*.png, relues |
| Débordement des KPI (1440, 1280, 1200, 1100, 1024, 390) | aucun |
| Toucher : 1er tap verso, 2e tap recto | OK |
| Clavier : focus = anneau seul, Entrée = verso (aria-pressed), Tab = retour recto | OK |
| Menu ⋯ : données (tableau), agrandir (modale + titre), bascule Barres / Courbe | OK |

## Relecture indépendante : défauts corrigés
- B1 recto KPI qui débordait (ligne leader écrasée) : `flex-shrink:0`, ellipsis, libellé sur 1 ligne,
  indice masqué de 1200 à 1439 px, test avec libellé long.
- B2 toucher : `:hover` limité à `@media (hover:hover)` ; retournement au toucher via `pointerup`.
- I3 clavier : focus = anneau seul, Entrée / Espace bascule, `focusout` remet au recto, `aria-pressed`.
- I4 « Donnée indisponible » écrit sous le tiret (plus d'infobulle inaccessible).
- I5 héros accessible (plus de `role="img"`), liens-boutons sans `<a><button>` imbriqués.
- I6 liens de navbar nommés (`aria-label`) en mode icônes.
- I7 la navbar mobile se referme au changement de scène.
- I8 bascule mobile → bascule desktop synchronisées (source unique).
- I9 tableau des données : années non formatées, colonne Série masquée si vide, mention de troncature.
- I10 PNG exporté sur le fond de surface du thème.
- I11 cinémagraphe : boucle de pluie sans saut.
- M12 anneau de focus non doublé ; M13 modale titrée ; M14 menu masqué sans graphique ; M15 aria-label
  complet + indice « Toucher » sur écran tactile ; M16 `fmt_number` robuste à `pd.NA` / texte (tests) ;
  M17 démo : scène type servie sur `/paradoxe` ; M18 chiffre héros ramené au token `display` (64/68).

## Défauts mineurs restants
- Navbar en icônes : pas d'infobulle visible au survol (nom accessible présent).
- Burger : libellé accessible fixe (« Ouvrir la navigation ») même ouvert.
- À 390 px, « France métropolitaine » est tronqué dans le sélecteur (le libellé complet reste dans la liste).
- Dans les captures pleine page, la navbar fixe s'arrête à la hauteur de la fenêtre (artefact de capture).
