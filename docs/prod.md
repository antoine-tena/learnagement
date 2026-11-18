# La production

## Sauvegardes

En production, le conteneur `learnagement_data_mysql_backup_<instance>` sauvegarde la base
chaque jour à `BACKUP_AT` (02:00 par défaut, heure de Paris), avec `deploy/backup/backup.sh` :

- un fichier par jour, `database/backup/learnagement_<AAAAMMJJ-HHMMSS>.sql.gz` : structure, données et
  triggers, cohérents (`--single-transaction`), lisible par son seul propriétaire ;
- les fichiers de plus de `BACKUP_RETENTION_DAYS` jours (30) sont supprimés ;
- une première sauvegarde est faite dès le premier démarrage du conteneur.

Les variables sont dans `deploy/env.skeleton` (`BACKUP`, `BACKUP_AT`, `BACKUP_DIRECTORY`,
`BACKUP_RETENTION_DAYS`, `BACKUP_MAX_AGE_HOURS`, `BACKUP_ALERT_URL`).

**Savoir si elles marchent.** Le conteneur passe `unhealthy` quand la dernière sauvegarde a
échoué ou date de plus de `BACKUP_MAX_AGE_HOURS` heures (26) :

```bash
docker ps --filter name=data_mysql_backup     # healthy / unhealthy
docker logs learnagement_data_mysql_backup_<instance>
```

Si `BACKUP_ALERT_URL` est rempli, chaque échec y est aussi envoyé en POST (champ `message`).

**Une sauvegarde tout de suite** (avant une mise à jour, par exemple) :

```bash
docker exec learnagement_data_mysql_backup_<instance> /bin/bash /opt/backup.sh once
```

Les sauvegardes sont sur le même serveur que la base : la copie hors du serveur reste à
mettre en place (T-44).

### Restaurer

La restauration se fait en `root` : les triggers ne peuvent pas être créés par l'utilisateur
`learnagement` (erreur 1419, `SUPER privilege`). Le mot de passe est lu dans le conteneur, il
n'est pas tapé.

1. Arrêter ce qui écrit dans la base (`backend`, `web`, `dashboards`), en gardant `data_mysql`.
2. Repartir d'une base vide, puis charger la sauvegarde choisie :

```bash
MYSQL=learnagement_data_mysql_<instance>
docker exec -i $MYSQL sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot -e \
  "DROP DATABASE $MYSQL_DATABASE; CREATE DATABASE $MYSQL_DATABASE;"'
gunzip -c database/backup/learnagement_<AAAAMMJJ-HHMMSS>.sql.gz \
  | docker exec -i $MYSQL sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot "$MYSQL_DATABASE"'
```

3. Relancer l'application (`python Learnagement.py start`).

Une restauration jamais essayée ne compte pas : la refaire sur une instance de test à chaque
rentrée, et noter ici sa date et sa durée.

| Date | Base | Durée | Vérification |
|---|---|---|---|
| 2026-11-17 | jeu libre `small_set`, 50 tables (55 Ko compressé) | 5 s | sommes de contrôle des 50 tables et 4 triggers identiques |

## Certificats

### auto-signé

Création d'un certificat autosigné.

```bash
# générer le certificat
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 3650 -nodes
```

```bash
# Renommer pour correspondre à ton SSL_DIR
mv cert.pem  certs/cert.pem
mv key.pem   certs/key.pem
```
Les problèmes classiques du certificat auto-signé :
- le  navigateur ne fait pas confiance à une autorité inconnue ;
- Firefox lève l'erreur `SSL_ERROR_RX_RECORD_TOO_LONG`.

La solution dépend de ton contexte.

---

### En dev local → `mkcert` (recommandé)

`mkcert` crée une autorité de certification locale reconnue par ton navigateur.

```bash
# Installer mkcert
sudo apt install mkcert        # Linux
brew install mkcert            # Mac
choco install mkcert           # Windows

# Installer l'autorité locale dans le navigateur
mkcert -install

# Générer le certificat pour ton domaine local
mkcert localhost 127.0.0.1 monapp.local
# génère localhost+2.pem et localhost+2-key.pem
```

```bash
# Renommer pour correspondre à ton SSL_DIR
mv localhost+2.pem     certs/cert.pem
mv localhost+2-key.pem certs/key.pem
```

✅ Plus d'avertissement dans le navigateur, valable pour toute la machine.

---

### En prod → Let's Encrypt (certificat reconnu officiellement)

```bash
# Via certbot
sudo apt install certbot
sudo certbot certonly --standalone -d mondomaine.com

# Les certs sont générés dans :
# /etc/letsencrypt/live/mondomaine.com/fullchain.pem
# /etc/letsencrypt/live/mondomaine.com/privkey.pem
```

Ou via **Caddy** qui gère Let's Encrypt automatiquement sans rien faire.
