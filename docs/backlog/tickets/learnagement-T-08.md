# learnagement#T-08 · Python : plus d'`except:` nu ni de date sans fuseau
- **Type**: improvement
- **Priority**: 🟡 normal
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: XS · **Owner**: — · **Due**: —
- **Origin**: `kiln score`, règles BARE-EXCEPT et NAIVE-DATETIMES

Recompté le 2026-11-18 : 2 `except:` nus et 13 dates sans fuseau, tous dans `dashboards/`.

- [x] `backend/` : 6 noms d'export horodatés sans fuseau, passés par `core.clock` (heure de Paris, testé) ; aucun `except:` nu (fix/t08-backend)
- [x] `launcher/` : rien à corriger, déjà en UTC ou `Europe/Paris`
- [ ] `dashboards/` : 2 `except:` nus (`auth.py`, `pages/modules_enseignant_view.py`), 13 `datetime.now()` / `datetime.today()` sans fuseau (`pages/stages_administratif/layout.py`, `pages/charge_administratif.py`, `pages/charge_enseignant.py`)
- [ ] `scraping/` : 0 trouvé ici (dates déjà en UTC), à confirmer côté scraping
