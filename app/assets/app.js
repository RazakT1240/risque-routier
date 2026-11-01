/* Comportements d'interface sans aller-retour serveur.
   1. Carte KPI retournable : le survol (pointeur fin) est géré en CSS ; le toucher et
      Entrée / Espace basculent la classe « on » (aria-pressed suit) ; quitter la carte
      au clavier la remet au recto.
   2. Comptage animé des valeurs KPI, uniquement au premier affichage d'une scène (§9),
      désactivé si prefers-reduced-motion.
   3. Export PNG d'une figure sur le fond de surface du thème courant (pas de transparence). */
(function () {
  function basculer(carte, etat) {
    var on = typeof etat === "boolean" ? etat : !carte.classList.contains("on");
    carte.classList.toggle("on", on);
    carte.setAttribute("aria-pressed", on ? "true" : "false");
  }

  document.addEventListener("pointerup", function (e) {
    if (e.pointerType !== "touch" && e.pointerType !== "pen") { return; }
    var carte = e.target.closest && e.target.closest(".kpi-flip");
    if (carte) { basculer(carte); }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Enter" && e.key !== " ") { return; }
    var carte = e.target.classList && e.target.classList.contains("kpi-flip") ? e.target : null;
    if (carte) { e.preventDefault(); basculer(carte); }
  });

  document.addEventListener("focusout", function (e) {
    var carte = e.target.classList && e.target.classList.contains("kpi-flip") ? e.target : null;
    if (carte) { basculer(carte, false); }
  });

  var reduit = window.matchMedia("(prefers-reduced-motion: reduce)");
  var dejaVues = new Set();
  var fmt = new Intl.NumberFormat("fr-FR");

  function animer(el) {
    var cible = parseFloat(el.getAttribute("data-count"));
    var texteFinal = el.textContent;
    if (isNaN(cible) || !Number.isInteger(cible) || cible < 10) { return; }
    var debut = null;
    var duree = 700;
    function pas(t) {
      if (debut === null) { debut = t; }
      var p = Math.min((t - debut) / duree, 1);
      var v = Math.round(cible * (1 - Math.pow(1 - p, 3)));
      el.textContent = p < 1 ? fmt.format(v) : texteFinal;
      if (p < 1) { requestAnimationFrame(pas); }
    }
    requestAnimationFrame(pas);
  }

  var observateur = new MutationObserver(function () {
    if (reduit.matches) { return; }
    var chemin = window.location.pathname;
    if (dejaVues.has(chemin)) { return; }
    var valeurs = document.querySelectorAll(".kpi-value[data-count]");
    if (!valeurs.length) { return; }
    dejaVues.add(chemin);
    valeurs.forEach(animer);
  });
  observateur.observe(document.documentElement, { childList: true, subtree: true });

  window.routeExportPng = function (gd, nom) {
    if (!gd || !window.Plotly) { return; }
    var fond = getComputedStyle(document.documentElement).getPropertyValue("--bg-surface").trim();
    var layout = Object.assign({}, gd.layout, { paper_bgcolor: fond, plot_bgcolor: fond });
    window.Plotly.downloadImage({ data: gd.data, layout: layout },
      { format: "png", filename: nom, scale: 2, width: gd.offsetWidth, height: gd.offsetHeight });
  };
})();
