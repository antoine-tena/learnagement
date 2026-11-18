# components

Les morceaux de page réutilisables du web, un fichier PHP par composant. Une vue les appelle par
leur nom, avec leurs propriétés :

```php
<?= $t->component("select", props: [
    "label" => "Filière",
    "options" => $filieres,
    "size" => "sm",
]) ?>
```

`utils/template.php` trouve `components/<nom>.php` (un point dans le nom descend d'un dossier),
lui passe chaque propriété comme variable et y ajoute `$uuid`, un identifiant unique pour les
attributs `id`.

## Le catalogue

| Famille | Composants |
| --- | --- |
| Structure | `header`, `navbar`, `sidebar` (reçoit `urls`), `footer`, `card`, `divider`, `tabs` |
| Formulaires | `input`, `select`, `checkbox`, `radio`, `toggle`, `search_bar`, `button` |
| Retours | `alert`, `toast`, `badge`, `skeleton` (chargement) |
| Personnes | `avatar`, `avatar_group` |
| Démonstration | `howtouse.php` : une page autonome qui montre les composants (pas un composant) |

Les propriétés acceptées sont en tête de chaque fichier (`$label = $label ?? ''`). Les styles sont
dans `theme/theme/` (`buttons.css`, `forms.css`, `controls.css`, `surfaces.css`, `tokens.css`).

## Écrire un composant

- Une propriété absente a toujours une valeur par défaut : `$size = $size ?? null;`.
- Tout texte affiché passe par `htmlspecialchars` : une propriété peut venir de l'utilisateur.
- Pas d'appel à l'API ni de logique métier : un composant affiche ce qu'on lui donne.
- Un morceau propre à une seule page reste avec elle, dans `views/dashboard/<page>/`.
