# learnagement#T-46 · Phase A : les règles vérifiées partout
- **Type**: improvement
- **Priority**: 🟠 important
- **Status**: in progress
- **Opened**: 2026-11-17
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: architecture cible (`docs/architecture.md`)

Avant de déplacer quoi que ce soit, la machine vérifie les règles dans tous les langages, pour que
les phases suivantes se relisent vite. Rien n'est déplacé ici.

- [x] La charte compte aussi le `.php` et le `.js` ([FILE-SIZE]), budget au niveau actuel (6)
- [x] ruff (lint et mise en forme) et mypy sur `dashboards/`, dans le pre-commit et la CI ; la
  dette, règle par règle et module par module, dans `dashboards/pyproject.toml`
- [ ] PHP-CS-Fixer et PHPStan sur `web/`, au niveau qui passe aujourd'hui, relevé ensuite
- [ ] Prettier et ESLint sur le JS de `web/`
- [ ] Les couches vérifiées : import-linter en Python, deptrac en PHP
- [ ] `openapi.json` exporté et versionné, vérifié en CI (le workflow `api-contract.yml`
  d'ion-repo, avec une commande d'export FastAPI) ; les routes cassées détectées (oasdiff), à
  proposer à ion-repo s'il ne le fait pas ([REPORT-TO-KILN])
- [x] Les hooks de pré-commit installés par `bootstrap.py`
- [ ] `no-commit-to-branch` protège `main` et `develop`, qui n'existe pas ici, mais ni `dev` ni
  `prerelease` : défaut d'un fichier généré, à corriger dans ion-repo ([REPORT-TO-KILN])
- [ ] La CI poste un commentaire par PR : règles, tests, routes cassées ou non, migrations,
  nouvelles dépendances
