# learnagement#T-55 · Le quota de places s'affiche sur la carte de mobilité
- **Type**: bug
- **Priority**: 🟡 normal
- **Status**: todo
- **Opened**: 2026-11-18
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: learnagement#T-54, vu par le test de la carte (`app/web/tests/mobility-map.test.mjs`)

`fetchStudentQuota` (`app/web/scripts/mobility-map/api.js`) appelle
`/api.php?path=/university/etudiant/<id>/quota?annee_scolaire=2025-2026` : le `?` et le `=`
sortent du motif de chemin de `app/web/api.php`, qui répond 400. Le bloc du quota de la filière ne
s'affiche donc jamais, campagne ouverte ou non ; l'année y est aussi écrite en dur.

- [ ] Faire passer les paramètres de requête par `api.php` jusqu'au backend (ou l'année dans le
      chemin), sans élargir le motif à n'importe quel caractère
- [ ] L'année scolaire en cours calculée, plus écrite en dur
- [ ] Le test de la carte attend un 200 et le bloc du quota visible
