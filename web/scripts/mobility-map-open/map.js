import { escapeHtml, getLanguageFlags } from './api.js';
import { wishedUniversities } from './wishes.js';

export const map = L.map('map').setView([48.85, 2.35], 4);

// In a flex layout, Leaflet can initialize before final dimensions are settled.
requestAnimationFrame(() => map.invalidateSize());

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(map);

export const markers = L.markerClusterGroup();

export function popupText(university) {
    const idSemestre = university.annee === 4 ? 8 : 9;
    const alreadyInWishes = wishedUniversities.has(`${university.id_partner_university}-${idSemestre}`);
    const uid = String(university.id_partner_university);
    const isSubmitted = Array.from(wishedUniversities.values()).some((w) => Boolean(w.submission_date) && w.submission_date !== 'null' && w.submission_date !== 'None');
    const assignment = window.MobilityMapState.assignment;

    window.MobilityMapState.popupState.set(uid, {
        photos: null,
        photoIndex: 0,
        streetView: null,
    });

    return `
        <div class="popup-tabs">
            <button id="tab-photos-${uid}" type="button" class="popup-tab" onclick="window.switchPopupTab('${uid}', 'photos')">Photos</button>
            <button id="tab-street-${uid}" type="button" class="popup-tab" onclick="window.switchPopupTab('${uid}', 'streetview')">StreetView</button>
        </div>
        <div id="panel-photos-${uid}" class="popup-panel hidden">
            <div class="popup-carousel">
                <div class="popup-photo-frame">
                    <img id="photo-image-${uid}" class="popup-photo" alt="Photo universite" />
                    <button id="photo-prev-${uid}" type="button" class="popup-carousel-btn left" onclick="window.prevPopupPhoto('${uid}')" disabled>‹</button>
                    <button id="photo-next-${uid}" type="button" class="popup-carousel-btn right" onclick="window.nextPopupPhoto('${uid}')" disabled>›</button>
                </div>
            </div>
            <p id="photo-caption-${uid}" class="popup-photo-caption"></p>
            <p id="photo-status-${uid}" class="popup-status">Chargement des photos...</p>
        </div>
        <div id="panel-street-${uid}" class="popup-panel hidden">
            <div id="streetview-${uid}" class="popup-streetview"></div>
            <p id="street-status-${uid}" class="popup-status">Chargement du Street View...</p>
            <div class="popup-streetview-actions">
                <button id="street-open-${uid}" type="button" class="popup-streetview-expand" onclick="window.openStreetViewModal('${uid}')" disabled>Ouvrir en grand</button>
            </div>
        </div>
        <b>${escapeHtml(university.name)}</b> (${escapeHtml(university.code)})<br/>
        <em class="text-[0.75rem]">${escapeHtml(university.address)}, ${escapeHtml(university.country)}</em><br/>
        ${getLanguageFlags(university.languages)}<br/>
        S${university.annee == 4 ? '8' : '9'} :
        ${escapeHtml(university.number_of_places)} place${university.number_of_places > 1 ? 's' : ''}<br/>
        ${university.note_min !== null ? `Note min : ${university.note_min}<br/>` : ''}
        <a href="${escapeHtml(university.website)}" target="_blank">${escapeHtml(university.website)}</a><br/>
        ${
            (assignment && String(assignment.id_partner_university) === uid) ?
                (assignment.status === 'pending' ? `
                    <div class="mt-3 flex gap-2">
                        <button onclick="window.submitDecision('declined')" class="flex-1 px-2 py-1.5 bg-red-100 hover:bg-red-200 text-red-700 text-xs font-semibold rounded border border-red-200 transition">Refuser</button>
                        <button onclick="window.submitDecision('accepted')" class="flex-1 px-2 py-1.5 bg-green-600 hover:bg-green-700 text-white text-xs font-semibold rounded shadow-sm transition">Accepter</button>
                    </div>
                ` : assignment.status === 'accepted' ? `
                    <div class="mt-3 text-xs font-semibold p-2 rounded text-center bg-green-50 text-green-700 border border-green-200">Affectation acceptée</div>
                ` : `
                    <div class="mt-3 text-xs font-semibold p-2 rounded text-center bg-red-50 text-red-700 border border-red-200">Affectation refusée</div>
                `)
            : window.MobilityMapState.campaignOpen === false ? `
                <div class="mt-2 inline-flex items-center gap-1.5 rounded bg-gray-100 border border-gray-200 px-3 py-1.5 text-xs font-semibold text-gray-500 cursor-not-allowed">
                    <span>⏳</span> Disponible après le lancement de la campagne
                </div>
            ` : `
                <button
                    type="button"
                    onclick="window.addUniversityToWishes('${uid}', ${university.annee === 4 ? 8 : 9})"
                    ${alreadyInWishes || wishedUniversities.size >= 5 || isSubmitted ? 'disabled' : ''}
                    class="mt-2 inline-flex items-center rounded bg-primary px-3 py-1.5 text-sm font-semibold text-white hover:opacity-90 cursor-pointer disabled:cursor-not-allowed disabled:opacity-60"
                >
                    ${alreadyInWishes ? 'Déjà dans les voeux' : isSubmitted ? 'Voeux déjà soumis' : wishedUniversities.size < 5 ? 'Ajouter aux voeux' : 'Maximum de voeux atteint'}
                </button>
            `
        }
    `;
}

export function flyToUniversity(uid) {
    const university = window.MobilityMapState.universitiesById.get(String(uid));
    if (!university) return;

    const marker = window.MobilityMapState.markerInstances && window.MobilityMapState.markerInstances.get(String(uid));
    if (marker) {
        markers.zoomToShowLayer(marker, () => {
            marker.openPopup();
        });
        document.getElementById('wishesPanel').classList.add('hidden');
    } else {
        document.getElementById('semestreSelect').value = 'Tous';
        document.getElementById('filiereSelect').value = 'Toutes';
        const range = document.getElementById('noteMinRange');
        range.value = 20;
        document.getElementById('noteMinValue').innerText = 20;
        updateMap();

        setTimeout(() => {
            flyToUniversity(uid);
        }, 100);
    }
}

export function updateMap(universities) {
    const list = universities || window.MobilityMapState.universities || [];
    markers.clearLayers();
    window.MobilityMapState.markerInstances = new Map();

    const assignment = window.MobilityMapState.assignment;
    if (assignment) {
        const u = window.MobilityMapState.universitiesById.get(String(assignment.id_partner_university));
        if (u) {
            const marker = L.marker([u.latitude, u.longitude]).bindPopup(popupText(u));
            marker.on('popupopen', () => void window.hydratePopupContent(u));
            window.MobilityMapState.markerInstances.set(String(u.id_partner_university), marker);
            markers.addLayer(marker);
        }
        map.addLayer(markers);
        return;
    }

    const selectedSemestre = document.getElementById('semestreSelect').value;
    const selectedNote = parseFloat(document.getElementById('noteMinRange').value);

    const filtered = list.filter((u) => {
        const uNote = u.note_min === null ? 0 : parseFloat(u.note_min);
        if (uNote > selectedNote) return false;

        if (selectedSemestre === 'S8') {
            return u.S8_total_places > 0;
        } else if (selectedSemestre === 'S9') {
            return u.S9_total_places > 0;
        } else {
            return true;
        }
    });

    filtered.forEach((university) => {
        const marker = L.marker([university.latitude, university.longitude])
            .bindPopup(popupText(university));

        marker.on('popupopen', () => {
            void window.hydratePopupContent(university);
        });

        window.MobilityMapState.markerInstances.set(String(university.id_partner_university), marker);
        markers.addLayer(marker);
    });
    map.addLayer(markers);
}
