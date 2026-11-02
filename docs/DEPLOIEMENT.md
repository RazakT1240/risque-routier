# Déploiement

Guide de mise en ligne de l'application « Risque routier » (Dash + gunicorn).
Le dépôt est **prêt au déploiement** : `Dockerfile`, `render.yaml`, `fly.toml`, et les
agrégats Parquet lus au runtime (`data/processed/`) sont versionnés. Les **données brutes**
restent hors du dépôt (G16) ; elles ne sont pas nécessaires pour faire tourner l'app.

Point d'entrée de production : `gunicorn app.app:server` (le serveur Flask exposé par
`app/app.py`). Le conteneur écoute sur `$PORT` (défaut `8050`).

---

## Option A — Render (le plus simple, tier gratuit)

### 1. Compte
1. https://render.com → **Sign in with GitHub** → *Authorize Render*
   (on peut limiter au seul dépôt `risque-routier`).
2. Vérifier l'e-mail si demandé.

### 2. Déploiement par Blueprint
- Soit le bouton **« Deploy to Render »** du README.
- Soit : Dashboard → **New +** → **Blueprint** → choisir `RazakT1240/risque-routier`.

Render lit `render.yaml`, voit un *Web Service* `risque-routier` (runtime **Docker**, plan
**Free**), génère `APP_SECRET`. Cliquer **Apply**.

### 3. Build (~5–10 min)
Clone → `docker build` (`pip install`, l'étape longue) → copie du code et des données →
`gunicorn`. Statut **Live** (pastille verte) = prêt.

### 4. Accès
URL du type `https://risque-routier.onrender.com` → page de connexion →
**`actuaire` / `risque2026`**.

### 5. Personnaliser les identifiants
Service → onglet **Environment** → modifier `APP_UTILISATEUR` / `APP_MOTDEPASSE` →
**Save** (redéploie automatiquement).

### Mise en veille du tier gratuit
Après 15 min sans visite, le service s'endort ; réveil ~30–50 s. Pour éviter :
plan **Starter** payant, un *ping* régulier (cron-job.org), ou **Fly.io** (option B).

### Déploiement headless (API, sans clic)
Avec une **clé API Render** (Account Settings → API Keys), on peut créer le service
sans l'interface :
```bash
export RENDER_API_KEY="rnd_xxx"
OWNER=$(curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
  https://api.render.com/v1/owners | python -c "import sys,json;print(json.load(sys.stdin)[0]['owner']['id'])")
curl -s -X POST https://api.render.com/v1/services \
  -H "Authorization: Bearer $RENDER_API_KEY" -H "Content-Type: application/json" \
  -d '{"type":"web_service","name":"risque-routier","ownerId":"'"$OWNER"'",
       "repo":"https://github.com/RazakT1240/risque-routier","branch":"master",
       "autoDeploy":"yes",
       "serviceDetails":{"env":"docker","plan":"free",
         "envSpecificDetails":{"dockerfilePath":"./Dockerfile"}}}'
```

---

## Option B — Fly.io (pas de mise en veille agressive)

Même `Dockerfile`, config dans `fly.toml`.
```bash
# installer flyctl : https://fly.io/docs/flyctl/install/
fly auth login
fly launch --no-deploy            # reprend fly.toml (ne pas écraser)
fly secrets set APP_SECRET="$(python -c 'import secrets;print(secrets.token_hex(32))')"
fly deploy
```
URL : `https://risque-routier.fly.dev`.

---

## Option C — N'importe quel hôte Docker

```bash
docker build -t risque-routier .
docker run -p 8050:8050 \
  -e APP_SECRET="$(python -c 'import secrets;print(secrets.token_hex(32))')" \
  risque-routier
# http://localhost:8050
```

---

## Variables d'environnement

| Variable | Rôle | Défaut |
| --- | --- | --- |
| `APP_SECRET` | clé de signature du cookie de session (**à définir en prod**) | valeur dev faible |
| `APP_UTILISATEUR` | identifiant de connexion | `actuaire` |
| `APP_MOTDEPASSE` | mot de passe | `risque2026` |
| `APP_AUTH` | `0` désactive la page de connexion | `1` |
| `PORT` | port d'écoute (fourni par l'hébergeur) | `8050` |

## Mises à jour

Chaque `git push` sur `master` redéclenche un déploiement automatique (Render et Fly).

## Dépannage

| Symptôme | Cause probable | Action |
| --- | --- | --- |
| worker tué au démarrage / `MemoryError` | mémoire du tier gratuit juste au chargement des Parquet | passer à un plan avec plus de RAM, ou alléger le chargement |
| `ModuleNotFoundError` | dépendance manquante | ajouter au `requirements.txt` |
| 502 / page blanche | port non lu | vérifier que l'app écoute sur `$PORT` (déjà géré) |
| build en timeout | `pip install` lent | relancer un *Manual Deploy* |
