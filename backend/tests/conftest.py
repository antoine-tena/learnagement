"""Variables d'environnement factices pour les tests.

Les modules de l'API lisent leur configuration à l'import ; sans le `.env` que génère le
lanceur, ils échouent avant le premier test. Ces valeurs ne servent qu'aux tests : aucune
ne touche une vraie base ni un vrai service. Une variable déjà définie est gardée.
"""

import os

TEST_ENVIRONMENT = {
    "SESSION_TIMEOUT": "3600",
    "JWT_SIGNING_KEY": "test-signing-key-of-at-least-32-bytes",
    "INSTANCE_SECRET": "test-instance-secret",
    "CAS_SERVICE_TOKEN": "test-cas-token",
    "MYSQL_SERVER": "localhost",
    "MYSQL_PORT": "3306",
    "MYSQL_DB": "learnagement_test",
    "MYSQL_USER_LOGIN": "test",
    "MYSQL_USER_PASSWORD": "test",
    "DOCKER_SSL_INTERNAL_DIR": "/tmp",
}

for name, value in TEST_ENVIRONMENT.items():
    os.environ.setdefault(name, value)
