/* Rendu des graphiques ECharts (options construites en Python, app/echarts.py).
 * Format français des valeurs, animation coupée si prefers-reduced-motion,
 * redimensionnement automatique, export PNG pour le menu ⋯ des cartes. */
(function () {
  var instances = {};
  var reduit = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function fmtFr(v, d, suffixe) {
    if (v === null || v === undefined || v === "-" || isNaN(v)) { return "—"; }
    return Number(v).toLocaleString("fr-FR", { minimumFractionDigits: d, maximumFractionDigits: d })
      .replace(/[  ]/g, " ") + (suffixe || "");
  }

  function preparer(charge) {
    var option = JSON.parse(JSON.stringify(charge.option || {}));
    var f = charge.fmt || { decimales: 0, suffixe: "" };
    var formater = function (v) { return fmtFr(v, f.decimales, f.suffixe); };
    option.animation = !reduit;
    if (option.tooltip) { option.tooltip.valueFormatter = formater; }
    (option.series || []).forEach(function (s) {
      if (s.type === "gauge") {
        if (s.detail && s.detail.show !== false) { s.detail.formatter = formater; }
        if (s.axisLabel && s.axisLabel.show !== false) {
          s.axisLabel.formatter = function (v) { return fmtFr(v, 0, ""); };
        }
      }
    });
    return option;
  }

  function dessiner(el, charge) {
    if (!el || !window.echarts || !charge) { return null; }
    var inst = window.echarts.getInstanceByDom(el) || window.echarts.init(el);
    inst.setOption(preparer(charge), true);
    if (!el._routeObs && window.ResizeObserver) {
      el._routeObs = new ResizeObserver(function () { inst.resize(); });
      el._routeObs.observe(el);
    }
    return inst;
  }

  window.routeEchart = function (nom, charge) {
    var el = document.getElementById("echart-" + nom);
    var ancien = instances[nom];
    if (ancien && ancien.getDom() !== el) { ancien.dispose(); }
    instances[nom] = dessiner(el, charge);
  };

  window.routeEchartModal = function (charge) {
    var el = document.getElementById("modal-echart");
    // La modale s'ouvre en fondu : on attend qu'elle ait sa taille
    setTimeout(function () { var i = dessiner(el, charge); if (i) { i.resize(); } }, 220);
  };

  window.routeEchartPng = function (nom) {
    var inst = instances[nom];
    if (!inst || inst.isDisposed()) { return false; }
    var fond = getComputedStyle(document.documentElement).getPropertyValue("--bg-surface").trim();
    var a = document.createElement("a");
    a.href = inst.getDataURL({ type: "png", pixelRatio: 2, backgroundColor: fond });
    a.download = nom + ".png";
    a.click();
    return true;
  };
})();
