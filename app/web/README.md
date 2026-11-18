# Le web

Le front principal, en PHP sous Apache. Il ne lit jamais la base : il appelle l'API
(`utils/apiProxy.php`, `api.php`).

- `index.php` et `utils/router.php` : l'entrée et les routes.
- `views/` : les pages ; `components/` : les morceaux de page ; `scripts/` : leur JavaScript ;
  `theme/`, `assets/` : styles et images.
- `tests/` : les tests Node du JavaScript et de la configuration d'Apache.
- `Containerfile`, `container/` (vhosts, PHP, entrypoint), `compose.yaml` : son conteneur.

```bash
app/web/tools/run.sh vendor/bin/phpstan analyse   # le PHP (PHP de la machine, sinon podman)
pnpm --dir app/web test                           # le JavaScript
```
