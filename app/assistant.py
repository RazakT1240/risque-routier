"""Assistant « RAG ancré » : récupération de fiches calculées depuis les données (G1).

Aucun modèle de langage, aucun appel externe : une base de fiches est construite une fois au
démarrage à partir des Parquet pré-agrégés (G15), chacune portant une réponse chiffrée, sa source
et la scène où la voir. À chaque question, on récupère les fiches les plus proches par une
recherche lexicale TF-IDF (cosinus) tolérante aux synonymes. Tout nombre affiché vient des données.
"""

from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass, field

from app import data_access as da
from app.components.format import fmt_number, fmt_pct, fmt_ratio
from pipeline import config as C
from pipeline.indicators import letalite, taux_gravite

SEUIL = C.SEUIL_EFFECTIF


@dataclass
class Fiche:
    cle: str
    titre: str
    reponse: str
    source: str
    scene_nom: str
    scene_path: str
    mots: str = ""          # mots-clés supplémentaires pour la recherche
    graph: dict | None = None   # spec numérique (indépendante du thème) du petit graphique
    tokens: list[str] = field(default_factory=list)

    def texte_indexe(self) -> str:
        return " ".join([self.titre, self.reponse, self.mots])


# --- Spécifications de graphiques (numériques, indépendantes du thème) -------

def _serie(annees, valeurs, unite, dec, pem=True) -> dict:
    return {"kind": "serie", "annees": list(annees), "valeurs": list(valeurs),
            "unite": unite, "dec": dec, "pem": pem}


def _barres(cats, vals, alerte, unite, dec, moyenne=None) -> dict:
    return {"kind": "barres", "cats": list(cats), "vals": list(vals), "alerte": alerte,
            "unite": unite, "dec": dec, "moyenne": moyenne}


def figure_fiche(graph: dict | None, scheme: str):
    """Construit la figure Plotly d'une fiche à l'affichage (avec le thème courant)."""
    if not graph:
        return None
    from app import figures as fig  # import tardif : plotly est lourd
    k = graph["kind"]
    if k == "serie":
        dec = graph["dec"]
        return fig.courbe_annotee(graph["annees"], graph["valeurs"], scheme,
                                  fmt=lambda v, d=dec: fmt_number(v, d),
                                  unite=graph["unite"], plus_est_mauvais=graph["pem"])
    if k == "barres":
        dec = graph["dec"]
        return fig.barres_categories(graph["cats"], graph["vals"], graph["moyenne"], scheme,
                                     alerte=graph["alerte"],
                                     fmt=lambda v, d=dec: fmt_number(v, d))
    if k == "classees":
        return fig.barres_classees(graph["noms"], graph["vals"], scheme, graph["unite"],
                                   n=graph.get("n", 10))
    return None


# --- Construction des fiches depuis les Parquet -----------------------------

def _national(nom: str, cols: list[str]):
    return da.table(nom).groupby("annee")[cols].sum()


def _fiches_annuelles() -> list[Fiche]:
    g = _national("s02_gravite", ["victimes", "tues", "hospitalises", "legers"])
    acc = _national("s02_accidents", ["accidents", "accidents_mortels"])
    fiches: list[Fiche] = []
    metriques = [
        ("tues", "tués", "usagers tués", "morts décès mortalité tué"),
        ("hospitalises", "blessés hospitalisés", "blessés hospitalisés (> 24 h)",
         "blessé hospitalisation grave"),
        ("victimes", "victimes", "victimes (tués + blessés)", "victime blessés total"),
    ]
    ans = list(C.ANNEES)
    serie = {col: [int(g.loc[y, col]) for y in ans] for col in ["tues", "hospitalises", "victimes"]}
    serie_acc = [int(acc.loc[y, "accidents"]) for y in ans]
    serie_let = [round(letalite(g.loc[y, "tues"], g.loc[y, "victimes"]), 2) for y in ans]
    for a in C.ANNEES:
        for col, lib, defn, syn in metriques:
            val = int(g.loc[a, col])
            fiches.append(Fiche(
                f"an-{a}-{col}", f"{lib.capitalize()} en {a}",
                f"En {a}, la France métropolitaine a compté {fmt_number(val)} {lib} "
                f"({defn}).", da.SOURCE_BAAC, "Vue d'ensemble", "/vue-ensemble",
                f"{a} bilan combien nombre {syn}",
                graph=_serie(ans, serie[col], lib, 0)))
        na = int(acc.loc[a, "accidents"])
        fiches.append(Fiche(
            f"an-{a}-accidents", f"Accidents corporels en {a}",
            f"En {a}, on a recensé {fmt_number(na)} accidents corporels en France "
            f"métropolitaine.", da.SOURCE_BAAC, "Accueil", "/",
            f"{a} bilan combien nombre accidents corporels",
            graph=_serie(ans, serie_acc, "accidents corporels", 0)))
        let = letalite(g.loc[a, "tues"], g.loc[a, "victimes"])
        fiches.append(Fiche(
            f"an-{a}-letalite", f"Létalité en {a}",
            f"En {a}, la létalité routière était de {fmt_number(let, 1)} tués pour 100 "
            f"victimes.", da.SOURCE_BAAC, "Vue d'ensemble", "/vue-ensemble",
            f"{a} létalité mortel gravité tués pour cent victimes",
            graph=_serie(ans, serie_let, "tués / 100 victimes", 1)))
    # Cumul et évolution tués
    tot = g.sum()
    fiches.append(Fiche(
        "cumul-total", "Bilan cumulé 2019–2025",
        f"Sur {da.LIBELLE_PERIODE_CUMUL}, la France métropolitaine a compté "
        f"{fmt_number(int(tot['tues']))} tués, {fmt_number(int(tot['hospitalises']))} blessés "
        f"hospitalisés et {fmt_number(int(tot['victimes']))} victimes au total.",
        da.SOURCE_BAAC, "Vue d'ensemble", "/vue-ensemble",
        "cumul total période somme 2019 2025 tués victimes blessés"))
    d = da.DERNIERE_ANNEE
    var = (g.loc[d, "tues"] / g.loc[da.PREMIERE_ANNEE, "tues"] - 1) * 100
    sens = "stable" if abs(var) < 1 else ("en hausse" if var > 0 else "en recul")
    fiches.append(Fiche(
        "evo-tues", "Les tués baissent-ils ?",
        f"Entre {da.PREMIERE_ANNEE} et {d}, le nombre de tués est {sens} "
        f"({fmt_pct(var, 1, signe=True)}) : {fmt_number(int(g.loc[da.PREMIERE_ANNEE,'tues']))} "
        f"en {da.PREMIERE_ANNEE}, {fmt_number(int(g.loc[d,'tues']))} en {d}.",
        da.SOURCE_BAAC, "Vue d'ensemble", "/vue-ensemble",
        "évolution tendance baisse hausse tués depuis 2019 progrès",
        graph=_serie(ans, serie["tues"], "tués", 0)))
    return fiches


def _fiches_paradoxe() -> list[Fiche]:
    g = da.table("s02_gravite")
    acc = da.table("s02_accidents")
    t = g.groupby("agg_lib")["tues"].sum()
    a = acc.groupby("agg_lib")["accidents"].sum()
    part_acc_en = a.get("En agglomération", 0) / a.sum() * 100
    part_tues_hors = t.get("Hors agglomération", 0) / t.sum() * 100
    # Facteur de létalité hors / en agglomération
    vic = g.groupby("agg_lib")["victimes"].sum()
    let_en = letalite(t["En agglomération"], vic["En agglomération"])
    let_hors = letalite(t["Hors agglomération"], vic["Hors agglomération"])
    facteur = let_hors / let_en
    # Routes départementales (part des tués)
    td = g.groupby("catr_groupe")["tues"].sum()
    ad = acc.groupby("catr_groupe")["accidents"].sum()
    part_dep_tues = td.get("Départementale", 0) / td.sum() * 100
    part_dep_acc = ad.get("Départementale", 0) / ad.sum() * 100
    p = da.LIBELLE_PERIODE_CUMUL
    cats_agg = ["En agglomération", "Hors agglomération"]
    td_ord = [float(td.get(c, 0)) for c in td.sort_values(ascending=False).index]
    return [
        Fiche("para-agglo", "Ville ou campagne : où sont les accidents et les morts ?",
              f"Sur {p}, {fmt_pct(part_acc_en, 0)} des accidents surviennent en agglomération, "
              f"mais {fmt_pct(part_tues_hors, 0)} des tués le sont hors agglomération : la ville "
              f"fait les accidents, la campagne fait les morts.",
              da.SOURCE_BAAC, "Le paradoxe", "/paradoxe",
              "agglomération ville campagne rural hors où accidents morts tués paradoxe",
              graph=_barres(cats_agg, [float(t.get(c, 0)) for c in cats_agg],
                            "Hors agglomération", "tués", 0)),
        Fiche("para-letalite", "Est-on plus souvent tué hors agglomération ?",
              f"Hors agglomération, une victime est {fmt_ratio(facteur, 1)} plus souvent tuée "
              f"qu'en ville ({fmt_number(let_hors, 1)} contre {fmt_number(let_en, 1)} tués pour "
              f"100 victimes, sur {p}).",
              da.SOURCE_BAAC, "Le paradoxe", "/paradoxe",
              "létalité agglomération campagne hors facteur risque mourir rural",
              graph=_barres(cats_agg, [round(let_en, 1), round(let_hors, 1)],
                            "Hors agglomération", "tués / 100 victimes", 1)),
        Fiche("para-departementales",
              "Les routes départementales sont-elles les plus meurtrières ?",
              f"Sur {p}, les routes départementales concentrent {fmt_pct(part_dep_tues, 0)} des "
              f"tués pour {fmt_pct(part_dep_acc, 0)} des accidents.",
              da.SOURCE_BAAC, "Le paradoxe", "/paradoxe",
              "route départementale nationale autoroute type réseau tués meurtrière",
              graph=_barres(td.sort_values(ascending=False).index.tolist(), td_ord,
                            "Départementale", "tués", 0)),
    ]


MODES = {
    "2RM": ("2RM", "deux-roues motorisés moto scooter motard"),
    "Voiture": ("voiture", "automobile auto véhicule léger"),
    "Piéton": ("piéton", "piétons marche à pied"),
    "Vélo": ("vélo", "cycliste bicyclette vélos"),
    "EDP": ("EDP", "trottinette engin de déplacement personnel trottinettes"),
}


def _fiches_modes() -> list[Fiche]:
    g = da.table("s02_gravite")
    tot_tues = g["tues"].sum()
    # Tués par mode (classés) pour le graphique partagé des fiches « mode »
    par_mode = g.groupby("type_usager")["tues"].sum().sort_values(ascending=False)
    cats = par_mode.index.tolist()
    vals = [float(v) for v in par_mode.values]
    fiches: list[Fiche] = []
    for mode, (lib, syn) in MODES.items():
        sous = g[g["type_usager"] == mode][["victimes", "tues", "hospitalises"]].sum()
        if sous["victimes"] < SEUIL:
            continue
        part = sous["tues"] / tot_tues * 100
        grav = taux_gravite(sous["tues"], sous["hospitalises"], sous["victimes"])
        fiches.append(Fiche(
            f"mode-{mode}", f"Risque des usagers « {lib} »",
            f"Sur {da.LIBELLE_PERIODE_CUMUL}, les usagers « {lib} » représentent "
            f"{fmt_pct(part, 0)} des tués ; {fmt_pct(grav, 0)} de leurs victimes sont tuées ou "
            f"hospitalisées (taux de gravité).",
            da.SOURCE_BAAC, "Qui", "/qui",
            f"mode déplacement usager {lib} {syn} part tués gravité exposé",
            graph=_barres(cats, vals, mode, "tués", 0)))
    return fiches


def _fiches_qui() -> list[Fiche]:
    age = da.table("s04_age")
    fiches: list[Fiche] = []
    # Hommes vs femmes : tués rapportés à la population (G5), comme la scène 04
    tues = age.groupby("sexe_lib")["tues"].sum()
    pop = da.table("expo_population").groupby("sexe")["population"].sum()
    if ({"Homme", "Femme"}.issubset(set(tues.index))
            and pop.get("Homme") and pop.get("Femme") and tues.get("Femme")):
        ratio = (tues["Homme"] / pop["Homme"]) / (tues["Femme"] / pop["Femme"])
        taux_h = tues["Homme"] / pop["Homme"] * 1e6
        taux_f = tues["Femme"] / pop["Femme"] * 1e6
        fiches.append(Fiche(
            "qui-sexe", "Les hommes sont-ils plus touchés que les femmes ?",
            f"Sur {da.LIBELLE_PERIODE_CUMUL}, rapporté à la population, un homme a "
            f"{fmt_ratio(ratio, 1)} plus de risque d'être tué sur la route qu'une femme.",
            da.SOURCE_INSEE, "Qui", "/qui",
            "homme femme sexe genre masculin plus exposé risque tués jeunes",
            graph=_barres(["Homme", "Femme"], [round(taux_h, 0), round(taux_f, 0)],
                          "Homme", "tués / million d'habitants", 0)))
    # Piétons âgés (mêmes classes 65+ que la scène 04)
    ages_65 = {c for c in C.CLASSES_AGE if c == "95+" or int(c.split("-")[0]) >= 65}
    pie = age[age["type_usager"] == "Piéton"]
    tot_pie = pie["tues"].sum()
    if tot_pie >= SEUIL:
        part = pie[pie["classe_age"].astype(str).isin(ages_65)]["tues"].sum() / tot_pie * 100
        fiches.append(Fiche(
            "qui-pietons-ages", "Qui sont les piétons tués ?",
            f"Sur {da.LIBELLE_PERIODE_CUMUL}, {fmt_pct(part, 0)} des piétons tués ont 65 ans "
            f"ou plus.",
            da.SOURCE_BAAC, "Qui", "/qui",
            "piéton âgé senior 65 ans vieux tués vulnérable"))
    return fiches


def _fiches_evolution() -> list[Fiche]:
    g = da.table("s02_gravite")
    a0, a1 = da.PREMIERE_ANNEE, da.DERNIERE_ANNEE
    fiches: list[Fiche] = []
    ans = list(C.ANNEES)
    for mode, (lib, syn) in MODES.items():
        s = g[g["type_usager"] == mode].groupby("annee")["victimes"].sum()
        if a0 not in s or a1 not in s or s.get(a0, 0) < SEUIL:
            continue
        v0, v1 = int(s[a0]), int(s[a1])
        if v0 == 0:
            continue
        var = (v1 / v0 - 1) * 100
        facteur = v1 / v0
        corps = (f"multipliées par {fmt_number(facteur, 1)}" if facteur >= 1.5
                 else f"en évolution de {fmt_pct(var, 0, signe=True)}")
        serie = [int(s.get(y, 0)) for y in ans]
        fiches.append(Fiche(
            f"evo-{mode}", f"Évolution des victimes « {lib} » depuis {a0}",
            f"Les victimes « {lib} » sont {corps} entre {a0} ({fmt_number(v0)}) et {a1} "
            f"({fmt_number(v1)}).",
            da.SOURCE_BAAC, "Ce qui change", "/evolution",
            f"évolution tendance {lib} {syn} depuis 2019 augmentation hausse baisse",
            graph=_serie(ans, serie, f"victimes « {lib} »", 0)))
    return fiches


def _fiches_territoires() -> list[Fiche]:
    t = da.table("ind_territoires")
    t = t[t["periode"] == da.LIBELLE_PERIODE_CUMUL].copy()
    valides = t.dropna(subset=["taux_tues_million"])
    valides = valides[valides["eff_tues_million"] >= SEUIL].sort_values(
        "taux_tues_million", ascending=False).reset_index(drop=True)
    n = len(valides)
    fiches: list[Fiche] = []
    if n:
        pire = valides.iloc[0]
        mieux = valides.iloc[-1]
        fiches.append(Fiche(
            "terr-palmares", "Quels départements sont les plus et les moins risqués ?",
            f"Sur {da.LIBELLE_PERIODE_CUMUL}, le risque de mourir sur la route va de "
            f"{fmt_number(mieux['taux_tues_million'], 0)} tués par million d'habitants "
            f"({mieux['nom_dep']}) à {fmt_number(pire['taux_tues_million'], 0)} "
            f"({pire['nom_dep']}).",
            da.SOURCE_INSEE, "Où et quand", "/ou-quand",
            "département classement palmarès pire plus risqué dangereux sûr carte tués million",
            graph={"kind": "classees", "noms": valides["nom_dep"].tolist(),
                   "vals": valides["taux_tues_million"].tolist(),
                   "unite": "tués / million", "n": 10}))
    for _, r in valides.iterrows():
        rang = int((valides["taux_tues_million"] > r["taux_tues_million"]).sum()) + 1
        fiches.append(Fiche(
            f"terr-{r['dep']}", f"Mortalité routière dans « {r['nom_dep']} »",
            f"Dans le département « {r['nom_dep']} » ({r['dep']}), sur "
            f"{da.LIBELLE_PERIODE_CUMUL}, on compte {fmt_number(r['taux_tues_million'], 0)} tués "
            f"par million d'habitants (rang {rang} sur {n}, du plus au moins touché).",
            da.SOURCE_INSEE, "Où et quand", "/ou-quand",
            f"département {r['nom_dep']} {r['dep']} tués million territoire local"))
    return fiches


def _fiches_meteo() -> list[Fiche]:
    try:
        m = da.modele("meteo")
    except FileNotFoundError:
        return []
    effets = m.get("effets", {})
    fiches: list[Fiche] = []

    def rr(cle):
        e = effets.get(cle, {})
        return e.get("rr") or (math.exp(e["coef"]) if "coef" in e else None)

    # Risque relatif par condition (sec = référence à 1), hors « première pluie »
    conditions = [(c, rr(c)) for c in effets
                  if c != "premiere_pluie" and rr(c) is not None]
    conditions.sort(key=lambda cv: cv[1])
    g_meteo = _barres([c for c, _ in conditions], [round(v, 2) for _, v in conditions],
                      conditions[-1][0] if conditions else None,
                      "risque relatif", 2, moyenne=1.0) if conditions else None
    pluie = rr("pluie faible") or rr("pluie")
    if pluie:
        sens = ("moins" if pluie < 1 else "plus")
        fiches.append(Fiche(
            "meteo-pluie", "La pluie provoque-t-elle plus d'accidents ?",
            f"À caractéristiques égales (modèle GLM), un jour de pluie compte {sens} d'accidents "
            f"qu'un jour sec (risque relatif {fmt_number(pluie, 2)}).",
            "Météo-France + ONISR (BAAC)", "Simulateur", "/simulateur",
            "météo pluie temps intempéries accidents risque relatif modèle jour sec",
            graph=g_meteo))
    pp = effets.get("premiere_pluie") or {}
    rr_pp = pp.get("rr") or (math.exp(pp["coef"]) if "coef" in pp else None)
    if rr_pp:
        bas = pp.get("ic_bas")
        haut = pp.get("ic_haut")
        signif = bas is not None and haut is not None and not (bas <= 1 <= haut)
        constat = ("est significativement plus élevé" if signif
                   else "n'est pas significativement différent")
        fiches.append(Fiche(
            "meteo-premiere-pluie", "Les premières pluies sont-elles plus dangereuses ?",
            f"Le risque d'accident un jour de première pluie après une période sèche {constat} "
            f"(risque relatif {fmt_number(rr_pp, 2)}).",
            "Météo-France + ONISR (BAAC)", "Simulateur", "/simulateur",
            "première pluie chaussée glissante danger sec sécheresse hypothèse météo"))
    return fiches


def _fiches_methode() -> list[Fiche]:
    return [
        Fiche("meth-sources", "D'où viennent les données ?",
              "Les chiffres viennent des fichiers BAAC de l'ONISR (accidents corporels 2019–2025), "
              "des populations INSEE et du parc de véhicules SDES. Aucun nombre n'est inventé : "
              "tout est recalculé depuis ces sources.",
              "BAAC · INSEE · SDES", "Méthode et données", "/methode",
              "source données méthode onisr insee sdes baac fiabilité d'où provenance"),
        Fiche("meth-seuil", "Pourquoi certains taux ne s'affichent pas ?",
              f"Un taux calculé sur moins de {SEUIL} victimes n'est pas affiché : l'effectif est "
              f"trop faible pour être fiable (il apparaît grisé).",
              "Règle de méthode (G6)", "Méthode et données", "/methode",
              "seuil effectif trop faible grisé masqué pourquoi pas de chiffre fiabilité"),
    ]


# --- Recherche lexicale TF-IDF ----------------------------------------------

# Synonymes ramenés à un mot canonique présent dans les fiches
SYNONYMES = {
    "mort": "tues", "morts": "tues", "mortalite": "tues", "deces": "tues", "tue": "tues",
    "tues": "tues", "decede": "tues", "decedes": "tues",
    "blesse": "hospitalises", "blesses": "hospitalises", "hospitalise": "hospitalises",
    "hospitalisation": "hospitalises", "hospitalises": "hospitalises",
    "victime": "victimes", "victimes": "victimes",
    "accident": "accidents", "accidents": "accidents", "corporel": "accidents",
    "corporels": "accidents",
    "letalite": "letalite", "mortel": "letalite", "mortelle": "letalite",
    "gravite": "gravite", "grave": "gravite", "graves": "gravite", "severite": "gravite",
    "moto": "2rm", "motos": "2rm", "scooter": "2rm", "motard": "2rm", "2rm": "2rm",
    "pieton": "pieton", "pietons": "pieton", "marche": "pieton",
    "velo": "velo", "velos": "velo", "cycliste": "velo", "cyclistes": "velo",
    "bicyclette": "velo",
    "edp": "edp", "trottinette": "edp", "trottinettes": "edp",
    "voiture": "voiture", "voitures": "voiture", "auto": "voiture", "automobile": "voiture",
    "agglomeration": "agglomeration", "agglo": "agglomeration", "ville": "agglomeration",
    "urbain": "agglomeration", "urbaine": "agglomeration",
    "campagne": "rural", "rural": "rural", "rurale": "rural",
    "departementale": "departementale", "departementales": "departementale",
    "nationale": "nationale", "autoroute": "autoroute", "route": "route", "routes": "route",
    "pluie": "pluie", "meteo": "meteo", "intemperie": "meteo", "intemperies": "meteo",
    "temps": "meteo",
    "homme": "homme", "hommes": "homme", "masculin": "homme",
    "femme": "femme", "femmes": "femme", "feminin": "femme",
    "jeune": "jeune", "jeunes": "jeune",
    "age": "age", "ages": "age", "senior": "age", "vieux": "age", "personnes": "age",
    "departement": "departement", "departements": "departement", "dep": "departement",
    "territoire": "departement",
    "source": "source", "sources": "source", "donnee": "source", "donnees": "source",
    "evolution": "evolution", "tendance": "evolution", "progression": "evolution",
    "combien": "combien", "nombre": "combien", "bilan": "bilan",
}
# Mots trop fréquents ignorés
VIDES = {"le", "la", "les", "un", "une", "des", "de", "du", "en", "et", "a", "au", "aux",
         "pour", "par", "sur", "dans", "est", "sont", "quel", "quelle", "quels", "quelles",
         "combien", "y", "t", "il", "elle", "on", "ce", "cette", "ces", "plus", "moins",
         "qui", "que", "quoi", "ou", "ont", "sa", "son", "ses", "leur", "leurs", "avec",
         "etre", "ete", "fait", "font", "donne", "moi", "je", "tu", "nous", "vous"}


def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def _tokens(texte: str) -> list[str]:
    brut = _strip_accents(texte.lower())
    brut = brut.replace("deux-roues", "2rm").replace("deux roues", "2rm")
    brut = brut.replace("week-end", "weekend").replace("premiere pluie", "premierepluie")
    sortie: list[str] = []
    for mot in re.findall(r"[a-z0-9]+", brut):
        if mot in VIDES:
            continue
        sortie.append(SYNONYMES.get(mot, mot))
    return sortie


def _vecteur(tokens: list[str], idf: dict) -> dict:
    if not tokens:
        return {}
    poids: dict[str, float] = {}
    for mot in tokens:
        if mot in idf:
            poids[mot] = poids.get(mot, 0.0) + 1.0
    for mot in poids:
        poids[mot] = poids[mot] / len(tokens) * idf[mot]
    norme = math.sqrt(sum(v * v for v in poids.values())) or 1.0
    return {m: v / norme for m, v in poids.items()}


# _FICHES et _INDEX sont construits paresseusement au premier appel
_FICHES: list = []
_IDX: dict = {}


def _assurer_index() -> None:
    if _FICHES and _IDX:
        return
    fiches = (_fiches_annuelles() + _fiches_paradoxe() + _fiches_modes() + _fiches_qui()
              + _fiches_evolution() + _fiches_territoires() + _fiches_meteo() + _fiches_methode())
    for f in fiches:
        f.tokens = _tokens(f.texte_indexe())
    df: dict[str, int] = {}
    for f in fiches:
        for mot in set(f.tokens):
            df[mot] = df.get(mot, 0) + 1
    n = len(fiches)
    idf = {mot: math.log((n + 1) / (c + 1)) + 1 for mot, c in df.items()}
    _FICHES.extend(fiches)
    _IDX.update({"idf": idf, "vecteurs": [_vecteur(f.tokens, idf) for f in fiches]})


def rechercher(question: str, k: int = 4, seuil: float = 0.06) -> list[dict]:
    """Retourne jusqu'à `k` fiches pertinentes (score de cosinus décroissant)."""
    _assurer_index()
    q = _vecteur(_tokens(question or ""), _IDX["idf"])
    if not q:
        return []
    scores = []
    for i, vec in enumerate(_IDX["vecteurs"]):
        s = sum(q.get(m, 0.0) * v for m, v in vec.items())
        if s > seuil:
            scores.append((s, i))
    scores.sort(reverse=True)
    return [{**_FICHES[i].__dict__, "score": round(s, 3)}
            for s, i in scores[:k]]


EXEMPLES = [
    "Combien de tués en 2025 ?",
    "Ville ou campagne : où sont les morts ?",
    "Quel département est le plus risqué ?",
    "Le risque des deux-roues",
    "La pluie fait-elle plus d'accidents ?",
    "Évolution des trottinettes depuis 2019",
]
