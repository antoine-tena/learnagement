// Apache ne sert aucun fichier caché : le .env de l'instance (mots de passe, clé JWT) est recopié
// à la racine du web, que lit config.php.
// pnpm --dir app/web test
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';

const CONTAINER_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', 'container');
const VIRTUAL_HOSTS = ['apache.conf', 'ssl.conf'];
const HIDDEN_FILES_DENIED = /<FilesMatch "\^\\\.">\s*Require all denied\s*<\/FilesMatch>/;

for (const virtualHost of VIRTUAL_HOSTS) {
    test(`${virtualHost} refuse les fichiers cachés`, () => {
        const config = readFileSync(join(CONTAINER_DIR, virtualHost), 'utf8');
        assert.match(config, HIDDEN_FILES_DENIED);
    });
}
