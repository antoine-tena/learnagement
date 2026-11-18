# learnagement#T-54 · Une seule carte de mobilité
- **Type**: improvement
- **Priority**: ⚪ background
- **Status**: todo
- **Opened**: 2026-11-18
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: learnagement#T-11, fermé une fois les fichiers géants découpés

`web/scripts/mobility-map/` et `web/scripts/mobility-map-open/` sont deux copies du même code :
`main.js` et `wishes.js` identiques, `map.js` diffère d'une ligne (la page ouverte remet le
filtre de filière à `Toutes`), `api.js` de quatre URL (slash au début ou à la fin du `path`
envoyé à `/api.php`).

- [ ] Vérifier, sur les deux pages, laquelle des formes d'URL l'API attend vraiment
- [ ] Un seul dossier de scripts, les différences passées en paramètre par chaque page
      (`mobility-map.php`, `mobility-map_open.php`)
