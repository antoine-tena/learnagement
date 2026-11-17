# learnagement#T-47 · Phase B : la nouvelle arborescence
- **Type**: improvement
- **Priority**: 🟠 important
- **Status**: blocked — waiting for learnagement#T-46
- **Opened**: 2026-11-17
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: architecture cible (`docs/architecture.md`)

Les dossiers prennent leur place cible (`app/`, `lab/`, `database/`, `deploy/`) par déplacements
purs (`git mv`) : une application par commit, sans changer ce que fait le code. L'arborescence se
fait valider par Flavien (`urgent.md`) : refusée, elle coûterait toute la phase.

- [ ] `backend/` → `app/api/`, `web/` → `app/web/`, `dashboards/` → `app/dashboards/`,
  `scraping/` → `app/importers/`
- [ ] `db/` → `database/` (`migrations/`, `open-data/`, `tools/`)
- [ ] `Containerfile` et `compose.yaml` dans le dossier de chaque application ;
  `docker/compose/` et `config/` → `deploy/`
- [ ] `frontend/` → `lab/javascript/nextjs/`, si learnagement#T-12 le retient
- [ ] Le lanceur, la CI, le pre-commit et `charter.toml` suivent les nouveaux chemins
- [ ] `docs/moved.md` : chaque ancien chemin et le nouveau, pour les branches en cours
- [ ] README, `CONTRIBUTING.md`, carte du `CLAUDE.md` à jour ; CODEOWNERS par zone
- [ ] Prévenir les contributeurs avant (learnagement#T-33)
