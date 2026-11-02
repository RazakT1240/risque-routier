/* Simulateur (scène 07) : calcul côté client à partir des coefficients du modèle logistique
   (data/processed/models/simulateur.json, transmis par un dcc.Store). Aucun chiffre en dur :
   tout vient du modèle. */
window.dash_clientside = Object.assign({}, window.dash_clientside, {
  simulateur: {
    calcul: function (type, ageIdx, sexe, nuit, pluie, hors, route, clics, m) {
      var comparer = (clics || 0) % 2 === 1;
      var nu = window.dash_clientside.no_update;
      if (!m || !m.coefs) { return [nu, nu, nu, nu, nu, nu, nu, nu, nu, nu, nu, nu]; }
      var classe = m.niveaux.classe_age[ageIdx] || m.references.classe_age;
      var profil = {
        type_usager: type, classe_age: classe, sexe_lib: sexe,
        agg_lib: hors ? "Hors agglomération" : "En agglomération",
        nuit: nuit ? "Oui" : "Non", meteo_cat: pluie ? "pluie faible" : "sec",
        catr_groupe: route
      };
      var eta = m.intercept;
      Object.keys(profil).forEach(function (v) {
        var c = (m.coefs[v] || {})[profil[v]];
        if (c) { eta += c.coef; }
      });
      var proba = 1 / (1 + Math.exp(-eta));
      // Référence : part observée de blessés graves parmi les usagers impliqués
      var pMoy = m.taux_observe;
      var ratio = proba / pMoy;

      var en = (m.lang === "en");
      var f1 = new Intl.NumberFormat(en ? "en-GB" : "fr-FR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
      var nbsp = " ";
      var ratioTxt = "×" + nbsp + f1.format(ratio);
      var probaTxt = en ? (f1.format(proba * 100) + " %") : (f1.format(proba * 100) + nbsp + "%");

      var phrase;
      if (en) {
        var ageEn = "aged " + classe.replace("-", "–").replace("+", " and over");
        var nomsEn = {
          "Piéton": "A pedestrian", "Vélo": "A cyclist", "EDP": "An e-scooter user",
          "2RM": "A motorcyclist", "Voiture": "A car occupant", "Utilitaire": "A van occupant",
          "Poids lourd": "A truck occupant", "Bus, car, tram": "A bus, coach or tram passenger",
          "Autre": "A user of another vehicle"
        };
        var mEn = [(nomsEn[type] || type) + " " + ageEn];
        mEn.push(nuit ? "at night" : "by day");
        mEn.push(pluie ? "in the rain" : "in dry weather");
        mEn.push(hors ? "outside built-up areas" : "in built-up areas");
        var routesEn = {
          "Autoroute": "on a motorway", "Nationale": "on a trunk road",
          "Départementale": "on a departmental road", "Communale": "on a local road",
          "Métropole urbaine": "on an urban-metropolis road", "Autre": "on another road"
        };
        mEn.push(routesEn[route] || route);
        phrase = mEn.join(", ") + ": probability of being killed or hospitalised of " +
          probaTxt + ", i.e. " + ratioTxt + " the average of involved users.";
      } else {
        var femme = sexe === "Femme";
        var noms = {
          "Piéton": femme ? "Une piétonne" : "Un piéton",
          "Vélo": femme ? "Une cycliste" : "Un cycliste",
          "EDP": femme ? "Une usagère de trottinette ou d'EDP" : "Un usager de trottinette ou d'EDP",
          "2RM": femme ? "Une motarde" : "Un motard",
          "Voiture": femme ? "Une occupante de voiture" : "Un occupant de voiture",
          "Utilitaire": femme ? "Une occupante d'utilitaire" : "Un occupant d'utilitaire",
          "Poids lourd": femme ? "Une occupante de poids lourd" : "Un occupant de poids lourd",
          "Bus, car, tram": femme ? "Une passagère de bus, car ou tram" : "Un passager de bus, car ou tram",
          "Autre": femme ? "Une usagère d'un autre véhicule" : "Un usager d'un autre véhicule"
        };
        var morceaux = [(noms[type] || type) + " de " + classe.replace("-", "–").replace("+", " ans et plus").replace(/^(\d+–\d+)$/, "$1 ans")];
        morceaux.push(nuit ? "la nuit" : "le jour");
        morceaux.push(pluie ? "sous la pluie" : "par temps sec");
        morceaux.push(hors ? "hors agglomération" : "en agglomération");
        var routes = {
          "Autoroute": "sur autoroute", "Nationale": "sur route nationale",
          "Départementale": "sur route départementale", "Communale": "sur voie communale",
          "Métropole urbaine": "sur route de métropole urbaine", "Autre": "sur une autre voie"
        };
        morceaux.push(routes[route] || route);
        phrase = morceaux.join(", ") + " : probabilité d'être tué ou hospitalisé de " +
          probaTxt + ", soit " + ratioTxt + " la moyenne des usagers impliqués.";
      }

      // Jauge logarithmique de ÷8 à ×32 (mêmes bornes que la page) : position en %
      var lo = Math.log(m.jauge ? m.jauge[0] : 1 / 8), hi = Math.log(m.jauge ? m.jauge[1] : 32);
      var pos = Math.max(0, Math.min(100, (Math.log(ratio) - lo) / (hi - lo) * 100));
      var classeMarqueur = "jauge-marqueur " + (ratio > 1 ? "jauge-haut" : "jauge-bas");

      var largeur = Math.max(pMoy, proba);
      var wMoy = (pMoy / largeur * 100).toFixed(1) + "%";
      var wProfil = (proba / largeur * 100).toFixed(1) + "%";

      // Verdict qualitatif (toujours doublé d'un texte : jamais la couleur seule, G12)
      var badge, badgeAlerte;
      if (ratio >= 2) { badge = en ? "Very high risk" : "Risque très élevé"; badgeAlerte = true; }
      else if (ratio >= 1.3) { badge = en ? "High risk" : "Risque élevé"; badgeAlerte = true; }
      else if (ratio >= 0.77) { badge = en ? "Close to average" : "Proche de la moyenne"; badgeAlerte = false; }
      else { badge = en ? "Lower risk" : "Risque plus faible"; badgeAlerte = false; }
      badge = badge + " · " + ratioTxt;
      var badgeCls = "sim-badge " + (badgeAlerte ? "sim-badge-alerte" : "sim-badge-neutre");

      return [
        ratioTxt, probaTxt, phrase,
        { left: pos.toFixed(1) + "%" }, classeMarqueur,
        { display: comparer ? "block" : "none" },
        { width: wMoy }, { width: wProfil },
        en ? (f1.format(pMoy * 100) + " %") : (f1.format(pMoy * 100) + nbsp + "%"), probaTxt,
        badge, badgeCls
      ];
    },
    vehicule: function (type, m) {
      var fichiers = {
        "Piéton": "pieton", "Vélo": "velo", "EDP": "edp", "2RM": "moto",
        "Voiture": "voiture", "Utilitaire": "utilitaire", "Poids lourd": "camion",
        "Bus, car, tram": "bus", "Autre": "autre"
      };
      var f = fichiers[type] || "autre";
      var alt = (m && m.lang === "en") ? "Illustration of the selected road-user profile"
        : "Illustration du profil d'usager sélectionné";
      return ["/assets/vehicules/" + f + ".svg", alt];
    },
    age: function (ageIdx, m) {
      if (!m) { return window.dash_clientside.no_update; }
      var c = m.niveaux.classe_age[ageIdx] || "";
      if (m.lang === "en") {
        return c.indexOf("+") >= 0 ? c.replace("+", " and over") : c.replace("-", "–") + " yrs";
      }
      return c.indexOf("+") >= 0 ? c.replace("+", " ans et plus") : c.replace("-", "–") + " ans";
    }
  }
});
