# T-43 · Le proxy CAS seulement en développement
- **Type**: task
- **Priority**: 🟡 normal
- **Status**: to verify — `backend/auth/`, `config/`
- **Opened**: 2026-11-17
- **Effort**: XS · **Owner**: — · **Due**: —
- **Origin**: réunion avec Flavien Vernier, 2026-11-17

L'université a autorisé l'application sur son CAS : le proxy qui passait par le site de
l'université n'est plus utilisé en production. Vérifier qu'il est désactivé dans `config/env.prod`
(ou l'équivalent) et le documenter comme outil de développement.
