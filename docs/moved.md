# Les chemins déplacés

En novembre 2026, les dossiers ont pris leur place cible ([architecture.md](architecture.md),
learnagement#T-47). Les fichiers ont été déplacés sans changer ce que fait le code : les routes de
l'API, les variables d'environnement et les commandes du lanceur sont les mêmes.

## Ancien chemin, nouveau chemin

| Avant | Après |
|---|---|
| `backend/` | `app/api/` |
| `web/` | `app/web/` |
| `dashboards/` | `app/dashboards/` |
| `scraping/` | `app/importers/` (le paquet garde son nom, `learnagement_scraping`) |
| `assistant/` | `app/assistant/` |
| `db/` | `database/` |
| `db/sql/` | `database/migrations/` |
| `db/freeData/` | `database/open-data/` |
| `docker/backend/Containerfile` | `app/api/Containerfile` |
| `docker/backend/entrypoint.sh` | `app/api/container/entrypoint.sh` |
| `docker/web/Containerfile` | `app/web/Containerfile` |
| `docker/web/` (`apache.conf`, `ssl.conf`, `lnm-php.ini`, `entrypoint.sh`) | `app/web/container/` |
| `docker/dashboards/Containerfile` | `app/dashboards/Containerfile` |
| `docker/dashboards/entrypoint.sh` | `app/dashboards/container/entrypoint.sh` |
| `docker/frontend/Containerfile` | `lab/javascript/nextjs/Containerfile` |
| `docker/frontend/entrypoint.sh` | `lab/javascript/nextjs/container/entrypoint.sh` |
| `docker/compose/backend.yml` | `app/api/compose.yaml` |
| `docker/compose/web.yml` | `app/web/compose.yaml` |
| `docker/compose/dashboards.yml` | `app/dashboards/compose.yaml` |
| `docker/compose/frontend.yml` | `lab/javascript/nextjs/compose.yaml` |
| `docker/compose/` (MySQL, sauvegarde, phpMyAdmin, ETL) | `deploy/compose/` |
| `docker/backup/`, `docker/phpmyadmin/` | `deploy/backup/`, `deploy/phpmyadmin/` |
| `docker/compose.yaml` (écrit par le lanceur) | `deploy/compose.yaml` |
| `config/env.skeleton`, `config/env.dev`, `config/env.prod` | `deploy/env.skeleton`, `deploy/env.dev`, `deploy/env.prod` |
| `frontend/` | `lab/javascript/nextjs/` (le front Next.js, absent de la production) |
| `openapi.json` | `app/api/openapi.json` |
| `certs/` (ignoré) | `deploy/certs/` |
| `scripts/ci/unverified-rules.txt` | `.github/unverified-rules.txt` |

Nouveaux dossiers, un README chacun en attendant leur contenu : `lab/` et un dossier par langage
(learnagement#T-50), `app/portal/` (learnagement#T-41), `archive/`, `database/fake-data/`,
`docs/adr/`.

## Une instance existante (la production comprise)

Les dossiers privés, ignorés par git, ne bougent pas seuls. Avant de récupérer la nouvelle
version, arrêter l'instance : le lanceur ne trouverait plus l'ancienne compose.

```bash
python Learnagement.py stop
git pull
mv db/data database/data
mv db/backup database/backup
mv db/docker-entrypoint-initdb.d database/docker-entrypoint-initdb.d
mkdir -p deploy && mv docker/log deploy/log
mv certs deploy/certs
# Les anciennes copies du .env (elles contiennent les mots de passe) : le lanceur recopie
# le .env dans les nouveaux dossiers au lancement.
rm -f backend/.env web/.env dashboards/.env docker/.env db/.env frontend/.env
python Learnagement.py start
```

`SSL_INTERNAL_DIR` et `SSL_EXTERNAL_DIR` d'un `.env` existant valent `./certs/…` : les passer à
`./deploy/certs/internal/` et `./deploy/certs/external/`, comme le fait un `.env` neuf. Le
`node_modules/` de Next se réinstalle dans `lab/javascript/nextjs/` au lancement.

Sans ces déplacements, le lanceur ne retrouve pas `database/data` : il le croit vide et propose les
données fictives (hors production). La base elle-même, dans son volume, n'est pas touchée.

`BACKUP_DIRECTORY` d'un `.env` existant vaut `../db/backup` : les sauvegardes iraient encore dans
`db/backup/`. Le passer à `../database/backup`, comme le fait un `.env` neuf.

Puis supprimer ce qui reste des anciens dossiers (`rmdir db docker` s'ils sont vides ; les
`node_modules/` et `.venv/` des anciens dossiers se recréent dans les nouveaux).

## Une branche en cours

git suit les fichiers déplacés : `git merge` de la branche d'intégration porte les modifications
d'une branche sur leurs nouveaux chemins. Un fichier créé par la branche dans un ancien dossier est
signalé en conflit, déjà rangé dans le nouveau dossier : le vérifier, puis `git add`.

```bash
git fetch
git merge origin/<branche d'intégration>
git status          # les conflits de dossiers renommés : vérifier, puis git add
```
