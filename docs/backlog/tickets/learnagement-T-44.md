# learnagement#T-44 · Les sauvegardes automatiques, et une restauration testée
- **Type**: bug
- **Priority**: 🔴 critical
- **Status**: blocked — waiting for Flavien (où vont les copies)
- **Opened**: 2026-11-17
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: lecture du code, 2026-11-17

La base de production, qui porte les stages et bientôt la mobilité d'environ 400 étudiants, est
sauvegardée chaque jour par le conteneur `data_mysql_backup` (`docker/backup/backup.sh`), et sa
restauration est essayée (`docs/prod.md`). Les copies restent sur le même serveur que la base,
et un échec ne prévient encore personne hors du serveur : deux décisions de Flavien
(`urgent.md`).

- [x] Écrire `backup.sh` : une sauvegarde par jour, une durée de conservation
- [ ] Une copie hors du serveur, dans un stockage que l'université accepte pour des données
  personnelles (décision dans `urgent.md`)
- [x] Restaurer une sauvegarde sur une instance de test, et décrire la marche à suivre dans
  `docs/prod.md`
- [x] Une alerte quand une sauvegarde échoue : sonde `unhealthy` et `BACKUP_ALERT_URL`
- [ ] Choisir où va l'alerte (mail, messagerie de l'équipe) et remplir `BACKUP_ALERT_URL`
