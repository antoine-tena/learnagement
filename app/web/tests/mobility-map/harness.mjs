// Charge le script d'une page de carte de mobilité dans Node, avec un DOM, Leaflet et fetch
// simulés, puis écrit sur la sortie ce que la page a fait (appels, marqueurs, éléments cachés).
// Usage : node harness.mjs <page PHP, depuis web/> <scénario : student|anonymous>
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

import { API_RESPONSES, AUTH_FREE_PATHS, INITIAL_VALUES } from './fixtures.mjs';

const WEB_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const [pagePath, scenario] = process.argv.slice(2);
const isAnonymous = scenario === 'anonymous';

const pageHtml = readFileSync(join(WEB_DIR, pagePath), 'utf8').replace(/<!--[\s\S]*?-->/g, '');
const elementIds = [...pageHtml.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]);
const initiallyHiddenIds = new Set(
    [...pageHtml.matchAll(/\sid="([^"]+)"[^>]*class="[^"]*\bhidden\b/g)].map((match) => match[1])
);
const scriptSrc = pageHtml.match(/<script type="module"[^>]*src="([^"]+)"/)[1];

function fakeElement(id) {
    const classes = new Set(initiallyHiddenIds.has(id) ? ['hidden'] : []);
    return {
        value: INITIAL_VALUES[id] ?? '',
        innerText: '',
        innerHTML: '',
        classList: {
            add: (name) => classes.add(name),
            remove: (name) => classes.delete(name),
            contains: (name) => classes.has(name),
        },
    };
}

const elements = new Map(elementIds.map((id) => [id, fakeElement(id)]));
const apiCalls = [];
const markerPositions = [];

// Le motif de chemin accepté par api.php.
const API_PATH_PATTERN = /^\/[a-zA-Z0-9_\-/]{1,255}$/;

// api.php refuse un chemin hors de son motif, puis le backend reçoit le chemin sans les « / » du
// début et de la fin ; sans connexion, seules les routes anonymes répondent.
function apiAnswer(path) {
    if (!API_PATH_PATTERN.test(path)) return { status: 400, body: { error: 'Invalid path' } };
    const backendPath = path.replace(/^\/+|\/+$/g, '');
    if (isAnonymous && !AUTH_FREE_PATHS.includes(backendPath)) {
        return { status: 401, body: { detail: 'Not authenticated' } };
    }
    const body = API_RESPONSES[backendPath.replace(/^university\/etudiant\/\d+/, 'university/etudiant/ID')];
    return body === undefined ? { status: 404, body: { detail: 'Not Found' } } : { status: 200, body };
}

globalThis.fetch = async (url, options = {}) => {
    const path = new URL(url, 'http://localhost').searchParams.get('path');
    const answer = apiAnswer(path);
    apiCalls.push(`${options.method ?? 'GET'} ${path} -> ${answer.status}`);
    return { ok: answer.status < 300, status: answer.status, json: async () => answer.body };
};

function fakeMarker(position) {
    const marker = { bindPopup: () => marker, on: () => marker, position };
    return marker;
}

globalThis.L = {
    map: () => ({ setView() { return this; }, invalidateSize: () => undefined, addLayer: () => undefined }),
    tileLayer: () => ({ addTo: () => undefined }),
    markerClusterGroup: () => ({
        clearLayers: () => markerPositions.splice(0),
        addLayer: (marker) => markerPositions.push(marker.position),
    }),
    marker: fakeMarker,
};
globalThis.window = globalThis;
globalThis.window.ENV = { USER_ID: isAnonymous ? '0' : '42' };
globalThis.document = { getElementById: (id) => elements.get(id) ?? null };
globalThis.requestAnimationFrame = () => undefined;
globalThis.setTimeout = () => undefined;
console.log = () => undefined;
console.error = () => undefined;

await import(pathToFileURL(join(WEB_DIR, scriptSrc)).href);

const hiddenElements = [...elements]
    .filter(([, element]) => element.classList.contains('hidden'))
    .map(([id]) => id)
    .sort();
process.stdout.write(JSON.stringify({
    scriptSrc,
    apiCalls,
    markerPositions,
    hiddenElements,
    wishesCount: elements.get('wishesCount')?.innerText,
}));
