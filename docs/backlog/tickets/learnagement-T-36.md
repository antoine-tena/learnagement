# learnagement#T-36 · Les appels de Next visent des routes qui existent
- **Type**: bug
- **Priority**: 🟡 normal
- **Status**: blocked — waiting for learnagement#T-40
- **Opened**: 2026-10-30
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: revue de l'architecture

7 appels sur 13 passent par `/api/proxy/list/*` et `/api/proxy/select/*`, pour lesquels une
recherche ne trouve aucune route du backend, sur aucune branche : `listApprentissagesCritiques`,
`listModulesOfAllAPC` (deux appels), `selectChargeEnseignant`, `selectSeance`, `selectMaquette`,
`listAPCbyIdModule`. Sont touchés : les charges, la maquette et une partie des modules. Confirmer
en lançant le front, puis brancher ces écrans sur les routes actuelles ou les créer.
