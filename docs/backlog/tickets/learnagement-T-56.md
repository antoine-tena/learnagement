# learnagement#T-56 · Le conteneur web sert le .env de l'instance
- **Type**: bug
- **Priority**: 🔴 critical
- **Status**: todo
- **Opened**: 2026-11-18
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: learnagement#T-47, reproduit en déplaçant le conteneur web

Le lanceur recopie le `.env` de l'instance (mots de passe MySQL, clé JWT, jeton CAS) dans le
dossier du web, monté comme racine d'Apache. Ni `app/web/container/apache.conf` ni
`app/web/.htaccess` ne le refusent : reproduit le 2026-11-18 sur une copie, avec l'image
`php:8-apache`, ces deux fichiers et un `.env` factice, `GET /.env` répond 200 et son contenu.

- [ ] Un test qui demande `/.env` (et tout fichier qui commence par un point) au conteneur web et
      attend 404 ou 403
- [ ] Apache refuse les fichiers cachés (`<FilesMatch "^\.">` dans `apache.conf`, pas seulement
      le `.htaccess`)
- [ ] Vérifier si la production le sert aujourd'hui ; si oui, changer les secrets du `.env` après
      le correctif (release à demander à Flavien)
- [ ] Le web lit ses variables sans copie du `.env` sous la racine d'Apache, si c'est possible
