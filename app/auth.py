"""Garde d'accès : page de connexion avant le tableau de bord.

Session Flask (cookie signé) ; identifiants par défaut surchargés par variables
d'environnement (APP_UTILISATEUR / APP_MOTDEPASSE / APP_SECRET). Aucun secret réel :
identifiants de démonstration affichés sur la page (projet portfolio public).

Couleurs injectées depuis design/tokens.py (G9 : aucun hexadécimal en dur ici).
"""

from __future__ import annotations

import os
from urllib.parse import quote

from flask import Response, redirect, request, session

from design.tokens import DARK, FONTS_URL, LIGHT

UTILISATEUR = os.getenv("APP_UTILISATEUR", "actuaire")
MOTDEPASSE = os.getenv("APP_MOTDEPASSE", "risque2026")
SECRET = os.getenv("APP_SECRET", "risque-routier-portfolio-dev")

# Chemins accessibles sans être connecté (page de connexion + ressources statiques).
_PUBLIC_PREFIXES = ("/assets/",)
_PUBLIC_EXACTS = ("/login", "/logout", "/_favicon.ico")

# Variables CSS utiles à la page de connexion, puisées dans les tokens (par mode).
_CLES = ("bg-page", "bg-surface", "bg-subtle", "border", "text-primary", "text-secondary",
         "text-muted", "accent", "accent-text", "accent-soft", "grav-tue", "delta-hausse-soft",
         "focus-ring", "on-accent", "shadow-eleve")

TEXTES = {
    "fr": {
        "titre": "Risque routier", "sous_titre": "Fréquence · Gravité · Coût",
        "accroche": "Accès au tableau de bord",
        "intro": "Espace réservé — présentation au comité de direction.",
        "label_id": "Identifiant", "label_mdp": "Mot de passe",
        "entrer": "Entrer", "erreur": "Identifiant ou mot de passe incorrect.",
        "demo": "Démonstration", "demo_id": "identifiant", "demo_mdp": "mot de passe",
        "pied": "Challenge Dataviz · Institut des Actuaires",
        "aria_id": "Identifiant", "aria_mdp": "Mot de passe",
    },
    "en": {
        "titre": "Road risk", "sous_titre": "Frequency · Severity · Cost",
        "accroche": "Dashboard access",
        "intro": "Restricted area — board-level presentation.",
        "label_id": "Username", "label_mdp": "Password",
        "entrer": "Sign in", "erreur": "Incorrect username or password.",
        "demo": "Demo", "demo_id": "username", "demo_mdp": "password",
        "pied": "Dataviz Challenge · Institut des Actuaires",
        "aria_id": "Username", "aria_mdp": "Password",
    },
}


def _css_variables() -> str:
    clair = ";".join(f"--{k}:{LIGHT[k]}" for k in _CLES if k in LIGHT)
    sombre = ";".join(f"--{k}:{DARK[k]}" for k in _CLES if k in DARK)
    return (f":root{{{clair};--radius:16px;--font-serif:Fraunces,Georgia,serif;"
            "--font-sans:Inter,system-ui,sans-serif}"
            f"@media (prefers-color-scheme:dark){{:root{{{sombre}}}}}")


def _langue() -> str:
    lg = request.args.get("lang") or request.cookies.get("langue") or "fr"
    return "en" if lg == "en" else "fr"


def page_login(erreur: bool, suivant: str, lang: str = "fr") -> str:
    t = TEXTES.get(lang, TEXTES["fr"])
    bloc_erreur = (f'<p class="err" role="alert">{t["erreur"]}</p>' if erreur else "")
    action = f'/login?next={quote(suivant, safe="/?=&")}'
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t["titre"]} · {t["accroche"]}</title>
<link rel="stylesheet" href="{FONTS_URL}">
<style>
{_css_variables()}
*{{box-sizing:border-box}}
body{{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
  padding:24px;background:var(--bg-page);color:var(--text-primary);
  font-family:var(--font-sans);-webkit-font-smoothing:antialiased}}
.carte{{width:100%;max-width:400px;background:var(--bg-surface);border:1px solid var(--border);
  border-radius:var(--radius);padding:36px 32px;box-shadow:var(--shadow-eleve)}}
.marque{{display:flex;align-items:center;gap:12px;margin-bottom:24px}}
.mono{{width:40px;height:40px;border-radius:10px;background:var(--accent);color:var(--on-accent);
  font-family:var(--font-serif);font-weight:600;font-size:22px;display:flex;
  align-items:center;justify-content:center}}
.marque h1{{font-family:var(--font-serif);font-size:19px;margin:0;line-height:1.1}}
.marque .sub{{font-size:11px;letter-spacing:.08em;text-transform:uppercase;
  color:var(--text-muted);margin-top:2px}}
.accroche{{font-family:var(--font-serif);font-size:22px;margin:0 0 4px}}
.intro{{color:var(--text-secondary);font-size:14px;margin:0 0 24px}}
label{{display:block;font-size:12px;font-weight:600;letter-spacing:.04em;
  text-transform:uppercase;color:var(--text-secondary);margin:16px 0 6px}}
input{{width:100%;padding:11px 13px;font-size:15px;font-family:inherit;
  color:var(--text-primary);background:var(--bg-page);border:1px solid var(--border);
  border-radius:8px;outline:none;transition:border-color .15s,box-shadow .15s}}
input:focus{{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-soft)}}
button{{width:100%;margin-top:24px;padding:12px;font-size:15px;font-weight:600;
  font-family:inherit;color:var(--on-accent);background:var(--accent);border:0;
  border-radius:8px;cursor:pointer;transition:filter .15s}}
button:hover{{filter:brightness(1.05)}}
button:focus-visible{{outline:3px solid var(--focus-ring);outline-offset:2px}}
.err{{margin:16px 0 0;padding:10px 12px;font-size:13px;color:var(--grav-tue);
  background:var(--delta-hausse-soft);border:1px solid var(--grav-tue);border-radius:8px}}
.demo{{margin:22px 0 0;padding:12px 14px;background:var(--bg-subtle);border-radius:8px;
  font-size:12.5px;color:var(--text-secondary);line-height:1.6}}
.demo b{{color:var(--text-primary);font-variant-numeric:tabular-nums}}
.pied{{margin:24px 0 0;text-align:center;font-size:11px;letter-spacing:.06em;
  text-transform:uppercase;color:var(--text-muted)}}
.langues{{position:fixed;top:16px;right:20px;font-size:13px}}
.langues a{{color:var(--text-muted);text-decoration:none;padding:0 4px}}
.langues a.on{{color:var(--accent-text);font-weight:600}}
</style></head><body>
<nav class="langues" aria-label="Langue / Language">
  <a href="?lang=fr{_sep(suivant)}" class="{_on(lang,'fr')}">FR</a><span>·</span>
  <a href="?lang=en{_sep(suivant)}" class="{_on(lang,'en')}">EN</a>
</nav>
<form class="carte" method="post" action="{action}" autocomplete="on">
  <div class="marque"><div class="mono" aria-hidden="true">R</div>
    <div><h1>{t["titre"]}</h1><div class="sub">{t["sous_titre"]}</div></div></div>
  <h2 class="accroche">{t["accroche"]}</h2>
  <p class="intro">{t["intro"]}</p>
  <label for="utilisateur">{t["label_id"]}</label>
  <input id="utilisateur" name="utilisateur" type="text" required autofocus
    aria-label="{t['aria_id']}" autocomplete="username">
  <label for="motdepasse">{t["label_mdp"]}</label>
  <input id="motdepasse" name="motdepasse" type="password" required
    aria-label="{t['aria_mdp']}" autocomplete="current-password">
  {bloc_erreur}
  <button type="submit">{t["entrer"]}</button>
  <p class="demo">{t["demo"]} — {t["demo_id"]} <b>{UTILISATEUR}</b>,
    {t["demo_mdp"]} <b>{MOTDEPASSE}</b></p>
  <p class="pied">{t["pied"]}</p>
</form></body></html>"""


def _sep(suivant: str) -> str:
    return f"&next={quote(suivant, safe='/?=&')}" if suivant and suivant != "/" else ""


def _on(lang: str, cible: str) -> str:
    return "on" if lang == cible else ""


def register(server) -> None:
    """Branche la garde d'accès et les routes /login et /logout sur le serveur Flask.

    `APP_AUTH=0` désactive la garde (QA automatisée, développement) : la page reste
    accessible mais /login et /logout restent définis."""
    server.secret_key = SECRET
    garde_active = os.getenv("APP_AUTH", "1") != "0"

    @server.before_request
    def _garde():
        if not garde_active:
            return None
        if session.get("auth"):
            return None
        chemin = request.path
        if chemin in _PUBLIC_EXACTS or chemin.startswith(_PUBLIC_PREFIXES):
            return None
        cible = request.full_path.rstrip("?") or "/"
        return redirect(f"/login?next={quote(cible, safe='/?=&')}")

    @server.route("/login", methods=["GET", "POST"])
    def login():
        lang = _langue()
        suivant = request.args.get("next") or "/"
        # Anti-redirection ouverte : uniquement un chemin interne (pas //, pas de schéma).
        if not suivant.startswith("/") or suivant.startswith("//") or "://" in suivant:
            suivant = "/"
        if request.method == "POST":
            u = (request.form.get("utilisateur") or "").strip()
            p = request.form.get("motdepasse") or ""
            if u == UTILISATEUR and p == MOTDEPASSE:
                session["auth"] = True
                session.permanent = True
                return redirect(suivant)
            return Response(page_login(True, suivant, lang), mimetype="text/html")
        return Response(page_login(False, suivant, lang), mimetype="text/html")

    @server.route("/logout")
    def logout():
        session.clear()
        return redirect("/login")
