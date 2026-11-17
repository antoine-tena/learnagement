# T-51 · Des données fictives pour travailler
- **Type**: improvement
- **Priority**: 🟡 normal
- **Status**: todo
- **Opened**: 2026-11-17
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: architecture cible (`docs/architecture.md`)

Le développement, la recette, la CI, le lab et les sessions Claude tournent sur des données
inventées, jamais réelles ([PERSONAL-DATA], [AI-CONFIDENTIALITY]). Les jeux de `db/freeData/` sont
figés ; un générateur produit des promos, des étudiants, des enseignants, des stages, des vœux de
mobilité et des absences cohérents, sur les maquettes publiques.

- [ ] Un générateur reproductible (graine fixe), en plusieurs tailles
- [ ] Le lanceur le propose au premier lancement, à côté des jeux libres
- [ ] Des comptes de test par rôle, listés dans le README
