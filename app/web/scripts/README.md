# scripts

Le JavaScript des pages du web, un dossier par page qui en a beaucoup.

| Chemin | Page | Contenu |
| --- | --- | --- |
| `mobility-admin/` | `dashboard/mobility-admin` | La gestion de la mobilité : campagne, universités, vœux, quotas, affectation, exports, diagnostics, carte. Point d'entrée `main.js`. |
| `mobility-map/` | `dashboard/mobility-map`, `mobility-map_open` | La carte de mobilité côté étudiant : universités, vœux, résultat d'affectation. Point d'entrée `main.js`. |
| `dependance_module/` | `dashboard/dependance_module` | Le Gantt des dépendances entre modules (DHTMLX) : données, filtres, fenêtre d'édition. |
| `liste_personnel.js` | `dashboard/liste_personnel` (annuaire) | La pagination de l'annuaire. |

La documentation de la mobilité : [docs/mobility/](../../../docs/mobility/technical.md).

## Les conventions

- **Modules ES** pour un dossier neuf : `main.js` chargé par
  `<script type="module" defer src="/scripts/<page>/main.js">`, qui importe le reste.
  `api.js` pour les appels, `state.js` pour l'état partagé, un fichier par partie de la page.
- **Appels à l'API** par le proxy du web, jamais vers l'API en direct :
  `fetch('/api.php?path=/university/admin/catalog')`. Le proxy ajoute le jeton de la session.
- **Anciens scripts** (`dependance_module/`) : chargés par `$t->script('dependance_module/gantt')`,
  en variables globales ; à passer en modules quand on y touche.
- Pas de bibliothèque chargée depuis un CDN sans empreinte d'intégrité (`integrity=`).

## Les tests

`pnpm --dir app/web test` lance les tests Node de `app/web/tests/` (la carte de mobilité y a les
siens). ESLint et Prettier se configurent dans `app/web/package.json`.
