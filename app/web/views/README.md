# views

Les pages du web. Une route de `index.php` rend une vue par son chemin sans `.php` :
`$t->render('dashboard/stage')` affiche `views/dashboard/stage.php`.

| Dossier | Contenu |
| --- | --- |
| `layouts/` | Les gabarits : `global.php` (le HTML commun), `base.php` (pages publiques), `dashboard.php` (pages connectées, barre latérale). |
| `base/` | Les pages publiques : accueil, connexion, première connexion (`init_password.php`), 404, sonde de santé. |
| `dashboard/` | Les pages connectées : stages, mobilité, dépendances entre modules, annuaire, rendus, profil, liens vers Dash et Next. |

## Les conventions

- **Gabarit** : une vue commence par `$t->extend('layouts/dashboard')` et remplit ses emplacements
  entre `$t->startSlot('title')` / `$t->endSlot()` (et `content`).
- **`@post/`** : le traitement du formulaire envoyé en POST sur la même route
  (`dashboard/@post/stage.php` pour `POST /dashboard/stage`).
- **`@stylesheet/`** : le CSS propre à une page, inclus par `$t->stylesheet('dashboard/@stylesheet/…')`.
- **Sous-dossier du nom de la page** (`mobility-admin/`, `stage/`) : les morceaux d'une page trop
  longue, inclus par la page du même nom.
- **Composants** : `$t->component('select', props: [...])`, voir [`../components/`](../components/README.md).
- **JavaScript** : dans [`../scripts/`](../scripts/README.md), jamais en long dans la vue.
- **Données** : par l'API seulement (`utils/apiProxy.php`, avec le jeton de `$user`), jamais de SQL.

## Ajouter une page

1. Écrire `views/dashboard/<page>.php` sur le gabarit `layouts/dashboard`.
2. Déclarer sa route dans `index.php`, avec `requireAuth` ou `requireRole` selon qui la voit.
3. L'ajouter à la barre latérale si elle doit y paraître : la liste `$urls` en tête de
   `layouts/dashboard.php`.

Une URL publiée est une interface : la renommer se signale dans le [README](../../../README.md).
