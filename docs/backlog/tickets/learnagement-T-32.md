# learnagement#T-32 · Des tests pour le front et les tableaux de bord
- **Type**: improvement
- **Priority**: ⚪ background
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: revue de l'arborescence

Seul `backend/` a une vraie suite de tests : couvrir au moins les parcours critiques du front
retenu par learnagement#T-12.

- [x] `dashboards/` : les parcours critiques testés (pages du menu, aiguillage des URL, client de
  l'API, jeton, calculs de dates), sans réseau ; `pytest` lancé par la CI
  (test/t32-dashboards-tests)
- [ ] Front : les parcours critiques du front retenu par learnagement#T-12
