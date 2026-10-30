# Archive

Code qui n'est plus lancé ni appelé, gardé pour mémoire au lieu d'être supprimé. Rien ici n'est
maintenu, testé ni vérifié par la charte (`charter.toml`, `exclude`) ; l'historique de chaque
fichier reste dans git (`git log --follow archive/<chemin>`).

| Chemin | Ce que c'était | Remplacé par |
|---|---|---|
| `phpbackend/` | L'ancien backend PHP (CRUD, listes, connexion), absent du docker-compose depuis février 2026 | `backend/` (API FastAPI) |
| `front_DashPlotly/multi_page_integration_example.py` | Exemple d'intégration multipage, jamais importé | `dashboards/main.py` |
| `scrapping/testIcal.py` | Essai de lecture d'un iCal, jamais appelé | `scraping/recup_agenda.py` |

Pour ressortir un fichier : `git mv archive/<chemin> <destination>`, puis le remettre aux règles
du repo.
