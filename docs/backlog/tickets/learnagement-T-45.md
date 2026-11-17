# learnagement#T-45 · phpMyAdmin hors de la production
- **Type**: bug
- **Priority**: 🟠 important
- **Status**: todo
- **Opened**: 2026-11-17
- **Effort**: XS · **Owner**: — · **Due**: —
- **Origin**: lecture du code, 2026-11-17

Le lanceur démarre phpMyAdmin en production (`launcher/config.py`, liste `prod`), sur un port
publié de l'hôte (`docker/compose/phpmyadmin.yml`) : une interface d'administration directe d'une
base qui contient des données personnelles, joignable depuis tout le VPN. Le retirer de la liste
`prod` ou, si Flavien en a besoin, ne l'ouvrir qu'en local par un tunnel SSH. Signaler le
changement dans le README.
