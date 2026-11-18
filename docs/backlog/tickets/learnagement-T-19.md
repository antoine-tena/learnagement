# learnagement#T-19 · Zod 4 et audit des dépendances du front
- **Type**: bug
- **Priority**: 🟠 important
- **Status**: in progress — branch fix/t19, since 2026-11-18
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: @antoine-tena · **Due**: —
- **Origin**: `pnpm audit` après learnagement#T-14

`pnpm audit` signale encore zod < 4.6.6 (élevée, dépendance directe en 3.x, version majeure à
passer), postcss-selector-parser par `@tailwindcss/typography` (modérée) et deepmerge par
`@svgr/webpack` (faible, sans correctif).

- [x] zod 4.6.7 (formulaire de connexion vérifié : mêmes messages d'erreur)
- [x] postcss-selector-parser ≥ 6.1.5 et minimatch ≥ 11.0.1 forcés par `overrides` (`frontend/pnpm-workspace.yaml`)
- [x] deepmerge : plus signalé par `pnpm audit`
- [ ] picomatch ≤ 4.0.7 (élevée, par `@tailwindcss/typography` > tailwindcss > micromatch) : aucune version corrigée publiée au 2026-11-18 ; à reprendre quand elle sort
