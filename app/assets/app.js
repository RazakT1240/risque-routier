/* Comportements d'interface sans aller-retour serveur.
   1. Carte KPI retournable : clic / toucher et Entrée / Espace basculent la classe « on ».
   2. Comptage animé des valeurs KPI, uniquement au premier affichage d'une scène (§9),
      désactivé si prefers-reduced-motion. */
(function () {
  function basculer(carte) {
    carte.classList.toggle("on");
  }

  document.addEventListener("click", function (e) {
    var carte = e.target.closest && e.target.closest(".kpi-flip");
    if (carte) { basculer(carte); }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Enter" && e.key !== " ") { return; }
    var carte = e.target.classList && e.target.classList.contains("kpi-flip") ? e.target : null;
    if (carte) { e.preventDefault(); basculer(carte); }
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
})();
