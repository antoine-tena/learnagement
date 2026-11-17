# learnagement#T-52 · Une production prête pour la charge
- **Type**: improvement
- **Priority**: 🟡 normal
- **Status**: todo
- **Opened**: 2026-11-17
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: architecture cible (`docs/architecture.md`), lecture du code, 2026-11-17

Le serveur sature déjà, selon Flavien. Le code montre des suspects : Dash lancé avec 2 processus
qui chargent chacun PyTorch par le RAG (learnagement#T-38), l'API qui relance sa suite de tests et `uv sync` à
chaque démarrage, production comprise (`docker/backend/entrypoint.sh`), le code monté en volume
dans les conteneurs.

- [ ] Mesurer la mémoire et le processeur de chaque conteneur
- [ ] Des images construites en CI ; plus de tests ni d'installation au démarrage
- [ ] Une API sans état, lancée en plusieurs copies derrière la porte d'entrée (learnagement#T-41)
- [ ] Une file de tâches persistée pour les exports Excel, les imports et l'assistant
  ([OUT-OF-REQUEST])
- [ ] OpenTelemetry pour les traces et les métriques, journaux structurés (learnagement#T-13)
- [ ] Une limite de mémoire par conteneur, des sondes de santé (learnagement#T-06)
