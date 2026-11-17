# learnagement#T-39 · La base passe de MySQL à Postgres
- **Type**: improvement
- **Priority**: 🟡 normal
- **Status**: todo
- **Opened**: 2026-11-17
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: réunion avec Flavien Vernier, 2026-11-17 ; architecture cible (`docs/architecture.md`)

Flavien veut passer à Postgres : un schéma par domaine (`docs/glossary.md`), la protection des
données personnelles ligne par ligne, des copies en lecture si la charge l'exige, et le moment de
renommer les tables. Ce qui sature le serveur aujourd'hui se mesure d'abord (learnagement#T-52). Remplace learnagement#T-26
(mise à jour de MySQL).

- [ ] Un schéma Postgres par domaine, les tables renommées d'après le glossaire
- [ ] SQLAlchemy et Alembic à la place des migrations `VX.Y.Z__*.sql` ([ORM], [MIGRATIONS]), à
  décider avec Flavien : ses conventions de base (`docs/db/README.md`) changent
- [ ] Migrer les données (pgloader), sur une copie d'abord
- [ ] Adapter le lanceur (`launcher/db.py` : initialisation, sauvegardes) et les fragments compose
- [ ] Coordonner avec les étudiants qui travaillent sur le déploiement automatique
- [ ] Signaler le changement dans le README (variables d'environnement, commandes du lanceur)
