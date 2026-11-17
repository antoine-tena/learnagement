# T-41 · La porte d'entrée : un domaine, une session, toutes les pages
- **Type**: idea
- **Priority**: ⚪ background
- **Status**: blocked — waiting for T-12
- **Opened**: 2026-11-17
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: réunion avec Flavien Vernier, 2026-11-17 ; architecture cible (`docs/architecture.md`)

Idée de Flavien : un seul front, où chacun contribue dans son langage. La cible la réalise en deux
parties : la porte d'entrée, ici, et le lab (T-50). Aujourd'hui, le PHP redirige vers Dash et Next
sur un autre port en posant un cookie (`web/views/dashboard/python.php`).

- [ ] Un proxy (Caddy) : un seul domaine, des chemins au lieu de ports (`/`, `/api/`,
  `/dashboards/`, `/assistant/`)
- [ ] La session CAS ouverte une fois, par l'API ; le proxy la vérifie avant de servir une page et
  transmet le jeton de l'utilisateur ([COOKIES])
- [ ] Les pages de Dash, puis celles du lab passées en production, affichées dans le cadre du web
- [ ] L'API revérifie les droits à chaque appel
- [ ] Plus tard : un jeton limité à ce qu'une page déclare lire, et LTI 1.3
