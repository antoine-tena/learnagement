# apc_dash

Les tableaux de bord de l'approche par compétences (APC) : compétences, apprentissages critiques
(AC), modules qui y contribuent, métiers visés. Tout passe par un seul item de menu,
« Approche par compétences » : le hub `apc_hub.py`, qui affiche un onglet par sous-page selon le
rôle (URL `/<rôle>/apc20_hub/<onglet>`).

## Les onglets

| Onglet | Module | Étudiant | Enseignant | Administratif |
| --- | --- | :-: | :-: | :-: |
| Analyse des compétences | `apc20_KPI.py` + `apc20_competence_ac/` | oui | oui | oui |
| Cartographie des compétences | `apc20_heatmap_apc/` | oui | | |
| Réseau Polytech | `app_reseaupolytech_etudiant/` | oui | | |
| Trajectoire d'étude | `apc20_trajectoire.py` | oui | | |
| Orientation par métier | `apc20_metier_orientation/` | oui | | |
| Assistant orientation | `polytech_rag/` (lit les PDF, sans index) | oui | | |
| Poids des modules | `apc20_poids_modules.py` | | oui | oui |
| Fiche module | `apc20_ens_fiche_module/` | | oui | |
| Couverture APC | `apc20_ens_couverture.py` | | oui | oui |
| Réseau et trous | `apc20_ens_reseau_gaps/` | | oui | oui |
| Ma contribution | `apc20_ens_contribution/` | | oui | |

La liste fait foi dans `apc_hub.py` (les onglets et, en bas, les onglets de chaque rôle).

## Le reste

- `apc20_layout.py` : les couleurs et styles communs ; `assets/` : les feuilles CSS.
- `apc20_ens_data_loader.py`, `apc20_ens_tools.py`, `apc20_heatmap_apc_tools.py`,
  `app_reseaupolytech_tools.py` : les appels à l'API partagés entre onglets.
- `apc20_chatbot.py`, `apc20_chatbot_backend.py`, `apc20_chatbot_tools/` : un chatbot APC (API
  Groq), **branché nulle part** pour l'instant.
- `app_metier_erreur.py` : une page d'essai, **branchée nulle part** non plus.

La recherche vectorielle qui remplacera la lecture directe des PDF est dans
[`app/assistant/`](../../assistant/README.md), pas encore en production.

## Ajouter un onglet

1. Créer un paquet `apc20_<sujet>/` : `layout.py`, `callbacks.py`, `queries.py` (appels à l'API),
   `__init__.py` qui réexporte le layout et `register_callbacks`.
2. L'ajouter au dictionnaire des onglets de `apc_hub.py`, puis aux rôles qui le voient.
3. Les mots (compétence, AC, niveau…) : le [glossaire](../../../docs/glossary.md).
