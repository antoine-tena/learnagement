import {
    callbacks,
    editableUniversities,
    escapeHtml,
    getLanguageFlags,
    universitiesById,
    wishesCountByUniversityId,
} from './state.js';

const map = L.map('map').setView([48.85, 2.35], 4);

// In a flex layout, Leaflet can initialize before final dimensions are settled.
requestAnimationFrame(() => map.invalidateSize());

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(map);

const markers = L.markerClusterGroup();

export function popupText(university) {
    const uid = String(university.id_partner_university);

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
        Demandes sur cette universite : ${escapeHtml(String(wishesCountByUniversityId.get(uid) || 0))}<br/>
        ${university.note_min !== null ? `Note min : ${university.note_min}<br/>` : ''}
        <a href="${escapeHtml(university.website)}" target="_blank">${escapeHtml(university.website)}</a><br/>

    `;
}

export function flyToUniversity(uid) {
    const university = universitiesById.get(String(uid));
    if (!university) return;

    const marker = window.MobilityMapState.markerInstances && window.MobilityMapState.markerInstances.get(String(uid));
    if (marker) {
        markers.zoomToShowLayer(marker, () => {
            marker.openPopup();
        });
    } else {
        // Le marqueur est filtré : on désactive les filtres pour l'afficher
        document.getElementById('semestreSelect').value = 'Tous';
        document.getElementById('filiereSelect').value = 'toutes';
        const range = document.getElementById('noteMinRange');
        range.value = 20;
        document.getElementById('noteMinValue').innerText = 20;
        updateMap();

        // On retente la navigation et l'ouverture lorsque la carte est à jour
        setTimeout(() => {
            flyToUniversity(uid);
        }, 100);
    }
}

export function scrollToUniversityOnMap(uid) {
    const mapSection = document.getElementById('mapSection');
    mapSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    window.setTimeout(() => {
        flyToUniversity(uid);
    }, 250);
}

export function updateMap() {
    markers.clearLayers();
    window.MobilityMapState.markerInstances = new Map();

    const selectedSemestre = document.getElementById('semestreSelect').value;
    const selectedFiliere = document.getElementById('filiereSelect').value;
    const selectedNote = parseFloat(document.getElementById('noteMinRange').value);

    const filtered = editableUniversities.filter((u) => {
        // Affiche univ si note_min <= selectedNote
        const uNote = u.note_min === null ? 0 : parseFloat(u.note_min);
        if (uNote > selectedNote) return false;

        if (selectedFiliere !== 'toutes' && (!u.filiereIds || !u.filiereIds.has(String(selectedFiliere)))) {
            return false;
        }

        // Filtre le semestre
        if (selectedSemestre === 'S8') {
            return u.annee === 4;
        } else if (selectedSemestre === 'S9') {
            return u.annee === 5;
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

callbacks.updateMap = updateMap;
