# learnagement#T-50 · Le lab : apprendre dans le langage de son choix
- **Type**: idea
- **Priority**: 🟡 normal
- **Status**: blocked — waiting for learnagement#T-47, learnagement#T-51
- **Opened**: 2026-11-17
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: architecture cible (`docs/architecture.md`)

`lab/` à la racine : un dossier par langage puis par framework, chacun avec le même kit
(`README.md`, `lab.toml`, `example/`, `template/`, `projects/`). Rien n'en part en production ; le
détail est dans `docs/architecture.md`.

- [ ] `lab/README.md` : le tableau pour choisir (langage, niveau, ce qu'on apprend, durée visée)
- [ ] Le kit des premiers frameworks : `php/vanilla`, `python/flask`, `python/dash`,
  `javascript/vanilla`, `javascript/react`, `javascript/nextjs`, `java/spring-boot`
- [ ] `python Learnagement.py lab new` et `lab run`, qui lisent `lab.toml`
- [ ] Un client de l'API généré par langage (OpenAPI Generator), jamais commité
- [ ] La suite de tests du contrat (Schemathesis) pour les projets de back
- [ ] La CI refuse un dossier sans kit et vérifie chaque projet avec les outils de son langage
- [ ] L'instance de recette affiche les projets du lab
- [ ] Les règles de passage en production et d'archivage, dans `lab/README.md`
