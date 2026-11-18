# learnagement#T-20 · Le front passe ESLint
- **Type**: improvement
- **Priority**: 🟡 normal
- **Status**: in progress — branch refactor/t20, since 2026-11-18
- **Opened**: 2026-10-30
- **Effort**: M · **Owner**: @antoine-tena · **Due**: —
- **Origin**: ESLint installé par learnagement#T-14

Le hook de commit vérifie chaque fichier touché, et `eslint .` trouve encore des erreurs
anciennes dans tout `frontend/` (`any`, `set-state-in-effect`, `prefer-const`) : le premier qui
modifie un de ces fichiers doit les corriger. À solder d'un coup. Ces erreurs sont gelées dans
`frontend/eslint-suppressions.json` depuis le 2026-11-17.

- [x] `prefer-const` (18)
- [x] `any` remplacés par des types (25)
- [x] `react-hooks/set-state-in-effect` (5) et `rules-of-hooks` (7, `maquetteModule.tsx`)
- [x] le reste : `no-unescaped-entities`, `display-name`, `no-require-imports`
- [x] `eslint-suppressions.json` supprimé, `eslint .` sans erreur
