# T-33 · Prévenir les contributeurs du refacto du fork
- **Type**: task
- **Priority**: 🟠 important
- **Status**: blocked — waiting for @antoine-tena : à lancer seulement sur sa demande
- **Opened**: 2026-10-30
- **Effort**: XS · **Owner**: @antoine-tena · **Due**: —
- **Origin**: demande d'Antoine, pour que les travaux en cours ne divergent pas du fork

À faire avant T-11 et T-29 : au 2026-10-30, le fork a 70 commits d'avance et 532 fichiers
modifiés par rapport à `dev`, et Flavien travaille surtout dans le backend, sous les anciens
chemins (`backend_python/`). Déplacer encore des fichiers rendrait la PR plus difficile à
intégrer. Lui signaler aussi T-34 et décider avec lui de T-12.

- [ ] En parler d'abord à Flavien : c'est son repo, et le fork lui propose ses changements par
  PR vers `dev`. Il est le seul à pouvoir prévenir les étudiants de cette année qui n'ont encore
  rien poussé.
- [ ] Ouvrir la PR en brouillon vers `dev` :
  https://github.com/FlavienVernier/learnagement/compare/dev...antoine-tena:learnagement:antoine-tena?expand=1
- [ ] Revoir les destinataires et les renommages du message, relevés le 2026-10-30.
- [ ] Poster le message, sous le compte d'Antoine et après son accord sur le texte :
  https://github.com/FlavienVernier/learnagement/issues/new

Les mentions notifient par GitHub, sans chercher d'e-mails dans les commits. Le message ne promet
pas que rien n'est supprimé : le diff compte 33 suppressions (dont `ToDo.md`, anciens scripts de
`scrapping/`) à vérifier, et les branches existantes risquent des conflits.

**Titre** : Refacto de structure en cours : où merger votre travail

> Bonjour @FlavienVernier @Houssam365 @maxencels576,
>
> Je fais une grosse réorganisation du repo sur mon fork, branche
> [`antoine-tena`](https://github.com/antoine-tena/learnagement/tree/antoine-tena) : dossiers
> renommés (`backend_python/` → `backend/`, `front_PHP/` → `web/`, `scrapping/` → `scraping/`…),
> tests et documentation. Le but n'est pas de retirer des fonctionnalités : le code est surtout
> déplacé, et le code mort va dans `archive/`.
>
> Pour éviter que nos travaux divergent, si vous avez du travail en cours, pouvez-vous le merger
> dans ma branche, ou ouvrir une PR vers elle ?
>
> ```
> git remote add antoine https://github.com/antoine-tena/learnagement.git
> git fetch antoine
> git merge antoine/antoine-tena
> ```
>
> Si un conflit vous bloque ou s'il vous manque quelque chose, dites-le ici et je m'en occupe.
> @FlavienVernier, je proposerai l'ensemble à `dev` par PR : dis-moi si tu préfères une autre
> organisation.
