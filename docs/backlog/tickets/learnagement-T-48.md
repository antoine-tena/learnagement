# T-48 · Phase C : découper et bien nommer, domaine par domaine
- **Type**: improvement
- **Priority**: 🟡 normal
- **Status**: blocked — waiting for T-47
- **Opened**: 2026-11-17
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: architecture cible (`docs/architecture.md`)

Chaque application prend le même rythme : `core/`, puis un dossier par domaine du glossaire
(`docs/glossary.md`). Un domaine par série de commits : on découpe et on renomme sans changer le
comportement, les tests passent avant et après. Regroupe T-11, T-29, T-31, T-27 et T-21.

- [ ] API : un paquet par domaine (`api.py`, `services.py`, `schemas.py`, `queries.py`,
  `tests/`) ; `core/` pour la configuration, la base, l'authentification et les droits
- [ ] Web : une page par dossier (`view.php`, `actions.php`, `js/`, `style.css`), rangée par domaine
- [ ] Tableaux de bord : un dossier par domaine, un fichier par rôle, sans préfixe `appNN_`
- [ ] Les noms du glossaire appliqués au code, sans toucher aux tables ni aux routes publiées
- [ ] La fabrique de routes déclare un schéma de réponse par requête
