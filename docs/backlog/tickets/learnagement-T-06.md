# learnagement#T-06 · Conteneurs : podman, utilisateur non root, images épinglées, sondes
- **Type**: improvement
- **Priority**: 🟠 important
- **Status**: in progress — branch feat/t06, since 2026-11-18
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: @antoine-tena · **Due**: —
- **Origin**: charte UV-PODMAN, `kiln score` IMAGES-BY-DIGEST, NON-ROOT-CONTAINERS, HEALTH-PROBES,
  SUPPORTED-RUNTIMES

`Containerfile` et `compose.yaml` (lus par podman comme par docker), lanceur par défaut sur
`podman compose`, `USER` non root, images de base par digest, `HEALTHCHECK` par service,
Node 18 (fin de vie) → Node LTS.

- [x] `Containerfile` par conteneur, `deploy/compose.yaml` écrit par le lanceur
- [x] Lanceur sur `podman` et `podman compose` par défaut (docker reste possible par le `.env`)
- [x] `USER` non root : backend, dashboards, frontend
- [ ] `USER` non root pour `web` : Apache écoute sur 80 et 443 ; des ports hauts (8080, 8443)
  changent `FRONT_PHP_DOCKER_PORT` et les vhosts, à essayer avant la prod
- [x] Images épinglées par digest (mysql, phpmyadmin, mageai, composer en plus de python et node)
- [x] Sonde par service lancé (phpmyadmin ajouté ; l'ETL n'est dans aucun environnement)
- [x] Node LTS : Node 26
- [x] Essai en dev sous podman (2026-11-18, sans `web`) : images construites, sondes saines,
  `start` prêt en 1 min 40 après correction du venv non root, d'uv sur le DNS de podman, de
  phpMyAdmin, de Next.js (`keep-id`) et de l'attente des sondes du lanceur
- [ ] Avant la release : podman sur le serveur de prod, ou la surcharge DOCKER_COMMAND dans son .env
