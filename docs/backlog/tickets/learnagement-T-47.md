# learnagement#T-47 · Phase B : la nouvelle arborescence
- **Type**: improvement
- **Priority**: 🟠 important
- **Status**: in progress — branch feat/t47-phase-nouvelle-arborescence, since 2026-11-18
- **Opened**: 2026-11-17
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: architecture cible (`docs/architecture.md`)

Les dossiers prennent leur place cible (`app/`, `lab/`, `database/`, `deploy/`) par déplacements
purs (`git mv`) : une application par commit, sans changer ce que fait le code. Antoine la mène sur
le fork et la montre ensuite à Flavien, qui décide s'il la reprend.

Les règles de learnagement#T-46 sont en place ; sa dernière case (`no-commit-to-branch` sur `dev`
et `prerelease`) se corrige dans ion-repo et ne touche aucun déplacement.

- [ ] `backend/` → `app/api/`, `web/` → `app/web/`, `dashboards/` → `app/dashboards/`,
  `scraping/` → `app/importers/`
- [ ] `db/` → `database/` (`migrations/`, `open-data/`, `tools/`)
- [ ] `Containerfile` et `compose.yaml` dans le dossier de chaque application ;
  `docker/compose/` et `config/` → `deploy/`
- [ ] `frontend/` → `lab/javascript/nextjs/`, si learnagement#T-12 le retient
- [ ] Le lanceur, la CI, le pre-commit et `charter.toml` suivent les nouveaux chemins
- [ ] `docs/moved.md` : chaque ancien chemin et le nouveau, pour les branches en cours
- [ ] README, `CONTRIBUTING.md`, carte du `CLAUDE.md` à jour ; CODEOWNERS par zone
