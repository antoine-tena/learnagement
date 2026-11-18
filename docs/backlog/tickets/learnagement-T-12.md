# learnagement#T-12 · Une seule API, une seule entrée, une seule authentification
- **Type**: idea
- **Priority**: ⚪ background
- **Status**: blocked — waiting for Flavien
- **Opened**: 2026-10-30
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: lecture du repo, revue de l'architecture

Trois fronts (PHP, Dash, Next) pour une seule application : Dash 11 233 lignes, PHP 9 720, Next
2 235. Flavien a une branche `refactor/nextJS_front` : décider avec lui la cible et le calendrier.

Proposition (`docs/architecture.md`) : aucun front ne remplace les autres. Une porte d'entrée
(learnagement#T-41) les réunit sous un domaine et une session ; le PHP et Dash restent en production ; Next,
absent de la production, part dans le lab (`lab/javascript/nextjs/`), d'où ses pages pourront
monter une à une. L'ancienne proposition (Next remplace le PHP page par page, learnagement#T-37) reste possible
si Flavien la préfère.

- [ ] Si Next part dans le lab : `frontend/` → `lab/javascript/nextjs/`, avec son conteneur (repris
      de learnagement#T-47, `docs/moved.md` à compléter)
