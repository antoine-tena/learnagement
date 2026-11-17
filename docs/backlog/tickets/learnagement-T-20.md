# learnagement#T-20 · Le front passe ESLint
- **Type**: improvement
- **Priority**: 🟡 normal
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: ESLint installé par learnagement#T-14

Le hook de commit vérifie chaque fichier touché, et `eslint .` trouve encore des erreurs
anciennes dans tout `frontend/` (`any`, `set-state-in-effect`, `prefer-const`) : le premier qui
modifie un de ces fichiers doit les corriger. À solder d'un coup.
