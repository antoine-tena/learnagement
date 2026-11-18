# Le lab

Ici, on apprend : on choisit un langage, on essaie, on se trompe, on recommence. Rien de `lab/`
n'entre dans une image de production ; ce qui tourne pour les utilisateurs est dans `app/`
([architecture](../docs/architecture.md)).

| Je veux… | Niveau | Dossier | Première page |
|---|---|---|---|
| le web côté serveur | débutant | `php/vanilla/` | 30 min |
| Python et les données | débutant | `python/flask/`, `python/dash/` | 30 min |
| JavaScript sans framework | débutant | `javascript/vanilla/` | 30 min |
| un framework front | intermédiaire | `javascript/react/`, `vue/`, `svelte/`, `nextjs/` | 1 h |
| un back typé | intermédiaire | `java/spring-boot/`, `csharp/aspnet/`, `go/net-http/`, `rust/axum/` | 2 h |

Aujourd'hui, seul `javascript/nextjs/` existe : le front Next.js, absent de la production. Les
autres dossiers et leur kit (`README.md`, `lab.toml`, `example/`, `template/`, `projects/`)
arrivent avec learnagement#T-50.

- Le lab tourne sur la vraie API et sur des données fictives, jamais sur des données réelles.
- Le lab suit les mêmes règles que `app/` (`charter.toml`) : les apprendre fait partie du travail.
- Une page qui respecte les règles, a ses tests, répond à un ticket et a un enseignant pour la
  parrainer monte dans `app/` par une PR de déplacement.
