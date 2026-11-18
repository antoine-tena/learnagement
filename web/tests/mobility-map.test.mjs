// La carte de mobilité de l'étudiant connecté, chargée avec une API simulée.
// pnpm --dir web test
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';

const HARNESS = join(dirname(fileURLToPath(import.meta.url)), 'mobility-map', 'harness.mjs');
const STUDENT_PAGE = 'views/dashboard/mobility-map.php';
const BOTH_UNIVERSITIES = [[10, 20], [30, 40]];

function runPage(pagePath, scenario) {
    return JSON.parse(execFileSync(process.execPath, [HARNESS, pagePath, scenario], { encoding: 'utf8' }));
}

test('la carte connectée montre les universités et les voeux de l’étudiant', () => {
    const page = runPage(STUDENT_PAGE, 'student');

    assert.deepEqual(page.apiCalls, [
        'GET /university/etudiant/42/campaign-status -> 200',
        'GET /university -> 200',
        'GET /university/etudiant/42/assignment -> 404',
        'GET /university/etudiant/42/wishes -> 200',
        'GET /university/etudiant/42/quota?annee_scolaire=2025-2026 -> 400',
    ]);
    assert.deepEqual(page.markerPositions, BOTH_UNIVERSITIES);
    assert.equal(page.wishesCount, '1/5');
    assert.deepEqual(page.hiddenElements, [
        'campaignClosedBanner', 'campaignClosedNotice', 'filterForm', 'studentQuotaContainer',
        'wishesEmpty', 'wishesPanel', 'wishesSubmittedBadge',
    ]);
});

test('la carte connectée, sans session, montre les universités sans voeux', () => {
    const page = runPage(STUDENT_PAGE, 'anonymous');

    assert.deepEqual(page.markerPositions, BOTH_UNIVERSITIES);
    assert.deepEqual(page.hiddenElements, [
        'campaignOpenBadge', 'filterForm', 'studentQuotaContainer', 'wishesBtn', 'wishesCount',
        'wishesEmpty', 'wishesList', 'wishesPanel', 'wishesSubmittedBadge',
    ]);
});
