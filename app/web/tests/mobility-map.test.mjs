// Les deux pages de carte de mobilité (connectée, publique) font la même chose avec le même code.
// pnpm --dir app/web test
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';

const HARNESS = join(dirname(fileURLToPath(import.meta.url)), 'mobility-map', 'harness.mjs');
const STUDENT_PAGE = 'views/dashboard/mobility-map.php';
const PUBLIC_PAGE = 'views/dashboard/mobility-map_open.php';
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

test('la carte publique montre les universités, sans voeux ni campagne', () => {
    const page = runPage(PUBLIC_PAGE, 'anonymous');

    assert.deepEqual(page.apiCalls, [
        'GET /university/etudiant/0/campaign-status -> 401',
        'GET /university -> 200',
        'GET /university/etudiant/0/assignment -> 401',
        'GET /university/etudiant/0/wishes -> 401',
    ]);
    assert.deepEqual(page.markerPositions, BOTH_UNIVERSITIES);
    assert.deepEqual(page.hiddenElements, [
        'campaignOpenBadge', 'filterForm', 'studentQuotaContainer', 'wishesCount',
        'wishesEmpty', 'wishesList', 'wishesPanel', 'wishesSubmittedBadge',
    ]);
});

test('les deux pages chargent le même script', () => {
    assert.equal(runPage(PUBLIC_PAGE, 'anonymous').scriptSrc, runPage(STUDENT_PAGE, 'anonymous').scriptSrc);
});
