# learnagement#T-19 · Zod 4 et audit des dépendances du front
- **Type**: bug
- **Priority**: 🟠 important
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: `pnpm audit` après learnagement#T-14

`pnpm audit` signale encore zod < 4.6.6 (élevée, dépendance directe en 3.x, version majeure à
passer), postcss-selector-parser par `@tailwindcss/typography` (modérée) et deepmerge par
`@svgr/webpack` (faible, sans correctif).
