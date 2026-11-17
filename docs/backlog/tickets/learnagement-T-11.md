# learnagement#T-11 · Les fichiers géants découpés
- **Type**: improvement
- **Priority**: 🟡 normal
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: charte FILE-SIZE

`backend/domains/lnm_university.py` (2 155 lignes, à commencer par lui),
`backend/domains/maquette_module.py` (1 312), `mobility-admin.php` (2 953), les deux cartes de
mobilité presque identiques (`mobility-map.php`, `mobility-map_open.php`). Un module par domaine,
tests d'abord (`/repo:modernize`), sans changer les routes. Le backend attend learnagement#T-33 ;
`mobility-admin.php` est migré en dernier (learnagement#T-12).

Fait partie des phases C et D (learnagement#T-48, learnagement#T-49).
