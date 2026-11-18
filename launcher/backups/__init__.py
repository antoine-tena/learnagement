"""La sauvegarde planifiée de la base : chaque jour à BACKUP_AT, en local ou sur un partage.

Pas encore branchée au lancement : `launch_backup_system()` est à appeler depuis `start`.

Variables d'environnement :
  BACKUP                   active le système (true/1/yes/on). Défaut : false
  BACKUP_AT                "HH:MM", heure de la sauvegarde quotidienne. Défaut : 00:00
  BACKUP_DIRECTORY         répertoire local. Défaut : database/backup
  BACKUP_REMOTE_DIRECTORY  répertoire distant monté le temps de la sauvegarde (prioritaire) :
                           //serveur/partage (cifs), serveur:/chemin (nfs),
                           utilisateur@serveur:chemin (sshfs), \\\\serveur\\partage (Windows)
  BACKUP_REMOTE_TYPE       force cifs | nfs | sshfs
  BACKUP_REMOTE_USER       utilisateur (cifs, Windows)
  BACKUP_REMOTE_PASSWORD   mot de passe (cifs, Windows)
  BACKUP_REMOTE_OPTIONS    options de montage supplémentaires (-o)
  BACKUP_REMOTE_SUDO       préfixe mount et umount par `sudo -n` (UNIX)
  BACKUP_RETENTION_DAYS    supprime les sauvegardes plus anciennes
"""

from launcher.backups.schedule import launch_backup_system, run_backup_once

__all__ = ["launch_backup_system", "run_backup_once"]
