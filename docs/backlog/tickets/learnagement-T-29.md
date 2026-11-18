# learnagement#T-29 · Le backend découpé par domaine
- **Type**: improvement
- **Priority**: ⚪ background
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: revue de l'arborescence, revue de l'architecture

Le backend est déjà presque rangé par domaine : `domains/` a un fichier par domaine, avec ses
routes et son SQL ; `repositories/` n'a qu'un fichier et `models/` trois petits. Il reste à faire
de ces fichiers des paquets aux noms de kiln (`app/api/app/<domaine>/api.py`, `services.py`,
règles [ROUTERS] et [SERVICES]), avec learnagement#T-11, sans changer les routes. Pas d'architecture
hexagonale : seule la logique complexe, comme l'affectation des mobilités, est isolée pour être
testée sans base.

Fait partie de la phase C (learnagement#T-48).
