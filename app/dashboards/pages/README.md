# pages

Les pages des tableaux de bord, une par vue et par rôle. Chaque page expose un layout et une
fonction `register_callbacks`, que `main_app/registry.py` importe et range dans le menu du rôle
(`administratif`, `enseignant`, `etudiant`). Aucune page ne lit la base : elles appellent l'API.

## Les vues

| Sujet | Pages | Clé du registre | Outils partagés |
| --- | --- | --- | --- |
| Absences | `absences_administratif`, `absences_enseignant`, `absences_etudiant` | `app3_*` | `absences_tools.py` |
| Notes | `notes_enseignant`, `notes_etudiant` | `app4_*` | `notes_tools.py` |
| Modules | `modules_enseignant_view`, `modules_enseignant_edit/` | `app5_*` | `modules_tools.py` |
| Charge de travail | `charge_administratif`, `charge_enseignant`, `charge_etudiant` | `app7_*` | `charge_tools.py` |
| Rendus | `rendus_etudiant` | `app9` | `rendus_tools.py` |
| Stages | `stages_administratif/`, `stages_enseignant`, `stages_etudiant` | `app10_*` | `stages_tools.py` |
| Dépendances entre séances | `dependances` (à mettre à jour), `dependances_new` | `app11`, `app11_new` | `dependances_tools.py` |
| MCCC | `mccc_administratif` | `app13_administratif` | `mccc_tools.py` |
| Contrôles de cohérence | `checks_administratif/` | `app14_administratif` | `checks_tools.py` |
| Compétences | `competences` | `app2` | `competences_tools.py` |

L'approche par compétences a son propre hub, dans [`../apc_dash/`](../apc_dash/README.md).

## La forme d'une page

- Une page simple : un fichier `<sujet>_<rôle>.py` (layout + callbacks), ses appels à l'API et ses
  calculs dans `<sujet>_tools.py`.
- Une page qui dépasse 300 lignes devient un paquet : `layout.py`, `callbacks.py`, `queries.py`
  (les appels à l'API), et `__init__.py` qui réexporte le layout et `register_callbacks`.

## Ajouter une page

1. Écrire la page et son `_tools.py`, en prenant les mots du [glossaire](../../../docs/glossary.md).
2. L'importer dans `import_apps()` de `main_app/registry.py`, sous une nouvelle clé.
3. L'ajouter au menu du rôle dans `build_menu_items()` (une icône dans `icon_map` si besoin).
4. Écrire ses tests dans `../tests/`.

Les clés `appN` sont dans les URL : en renommer une casse les liens déjà partagés.
