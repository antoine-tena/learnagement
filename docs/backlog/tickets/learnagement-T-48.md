# learnagement#T-48 · Phase C : découper et bien nommer, domaine par domaine
- **Type**: improvement
- **Priority**: 🟡 normal
- **Status**: blocked — waiting for learnagement#T-47
- **Opened**: 2026-11-17
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: architecture cible (`docs/architecture.md`)

Chaque application prend le même rythme : `core/`, puis un dossier par domaine du glossaire
(`docs/glossary.md`). Un domaine par série de commits : on découpe et on renomme sans changer le
comportement, les tests passent avant et après. Regroupe learnagement#T-11, learnagement#T-29, learnagement#T-31, learnagement#T-27 et learnagement#T-21.

- [ ] API : un paquet par domaine (`api.py`, `services.py`, `schemas.py`, `queries.py`,
  `tests/`) ; `core/` pour la configuration, la base, l'authentification et les droits
- [ ] Web : une page par dossier (`view.php`, `actions.php`, `js/`, `style.css`), rangée par domaine
- [ ] Tableaux de bord : un dossier par domaine, un fichier par rôle, sans préfixe `appNN_`.
  Restait le 2026-11-18 (repris de learnagement#T-27) : les fichiers de `dashboards/pages/`
  ont perdu leur préfixe (learnagement#T-31), mais ils restent à plat ; et les noms dans le
  code le gardent (`app10_administratif_layout`, `app11_new_dag`, `apc20_…` dans
  `dashboards/apc_dash/`). Les clés d'URL (`app10_administratif`…) sont publiées : elles ne
  changent pas, seul leur nom dans le code change.
- [ ] Les noms du glossaire appliqués au code, sans toucher aux tables ni aux routes publiées
- [ ] La fabrique de routes déclare un schéma de réponse par requête
