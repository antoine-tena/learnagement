# learnagement#T-32 · Des tests pour le front et les tableaux de bord
- **Type**: improvement
- **Priority**: ⚪ background
- **Status**: in progress — branch test/t32-dashboards-tests, since 2026-11-18
- **Opened**: 2026-10-30
- **Effort**: L · **Owner**: @antoine-tena · **Due**: —
- **Origin**: revue de l'arborescence

Seul `backend/` a une vraie suite de tests : couvrir au moins les parcours critiques du front
retenu par learnagement#T-12.

- [ ] `dashboards/` : les parcours critiques testés (pages du menu, aiguillage des URL, client de
  l'API, calculs de dates), sans réseau ; `pytest` lancé par la CI
- [ ] Front : les parcours critiques du front retenu par learnagement#T-12
