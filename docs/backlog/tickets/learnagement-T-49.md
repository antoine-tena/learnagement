# learnagement#T-49 · Phase D : réécrire le code qui doit l'être
- **Type**: improvement
- **Priority**: 🟡 normal
- **Status**: todo
- **Opened**: 2026-11-17
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: architecture cible (`docs/architecture.md`), lecture du code, 2026-11-17

Seulement ce que le découpage ne suffit pas à rendre lisible : des tests qui figent le comportement
actuel d'abord, puis la réécriture. Le plus simple après learnagement#T-48 ; le SQL et le code mort peuvent
partir avant.

- [ ] `mobility-admin.php` (2 953 lignes) : le JS en modules (indicateurs, tableau, filtres, exports)
- [ ] `mobility-map.php` et `mobility-map_open.php` (31 lignes de différence) : une seule page
- [ ] Les routes de plus de 100 lignes de la mobilité et des maquettes : route, service, requêtes
- [ ] Le SQL assemblé à la main (9 endroits, dont `lnm_university.py`, `lnm_calendar.py`,
  `init.py`) : des paramètres liés ([ORM])
- [ ] Le vieux code commenté (`api/dependencies.py`, `auth/authenticate_cas.py`…),
  `views/dashboard/test.php` et `app11_dag_dependance_new.py` : supprimés
- [ ] Le scraping n'écrit plus en base : il passe par des routes d'import de l'API
