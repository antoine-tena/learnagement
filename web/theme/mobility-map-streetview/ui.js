function getState(uid) {
    return window.MobilityMapState?.popupState?.get(String(uid)) ?? null;
}

async function hydratePopupContent(university) {
    const uid = String(university.id_partner_university);
    const state = window.MobilityMapState?.popupState?.get(uid);

    if (!state) {
        return;
    }

    state.university = university;
    state.photoIndex = 0;
    state.streetViewPosition = null;
    state.streetViewInitialized = false;
    state.photos = [];

    try {
        const found = await window.findPlaceByUniversity(university);
        const photos = Array.isArray(found.photos) ? found.photos.slice(0, 10) : [];
        window.MobilityMapCarousel?.setPopupPhotos(uid, photos);

        if (!photos.length) {
            const status = document.getElementById(`photo-status-${uid}`);
            if (status) {
                status.innerText = `Aucune photo trouvee (status API: ${found.status || 'UNKNOWN'}).`;
            }
        }
    } catch (error) {
        console.error('Erreur chargement photos:', error);
        const status = document.getElementById(`photo-status-${uid}`);
        if (status) {
            status.innerText = 'Impossible de charger les photos';
        }
    }

    state.streetViewPosition = await window.findStreetViewPosition(university);
    const streetStatus = document.getElementById(`street-status-${uid}`);
    const streetOpenBtn = document.getElementById(`street-open-${uid}`);

    if (streetStatus) {
        streetStatus.innerText = state.streetViewPosition
            ? 'Street View pret. Ouvrez l onglet StreetView.'
            : 'Street View indisponible a proximite';
    }
    if (streetOpenBtn) {
        streetOpenBtn.disabled = !state.streetViewPosition;
    }
}

function switchPopupTab(uid, tab) {
    const photosPanel = document.getElementById(`panel-photos-${uid}`);
    const streetPanel = document.getElementById(`panel-street-${uid}`);
    const photosTab = document.getElementById(`tab-photos-${uid}`);
    const streetTab = document.getElementById(`tab-street-${uid}`);

    if (!photosPanel || !streetPanel || !photosTab || !streetTab) {
        return;
    }

    const showPhotos = tab === 'photos';
    photosPanel.classList.toggle('hidden', !showPhotos);
    streetPanel.classList.toggle('hidden', showPhotos);
    photosTab.classList.toggle('active', showPhotos);
    streetTab.classList.toggle('active', !showPhotos);

    if (!showPhotos) {
        const state = getState(uid);
        const streetContainer = document.getElementById(`streetview-${uid}`);
        const streetStatus = document.getElementById(`street-status-${uid}`);
        console.log(uid, state, streetContainer, streetStatus);
        if (!state || !streetContainer || !streetStatus) {
            return;
        }

        if (!state.streetViewPosition) {
            streetStatus.innerText = 'Street View indisponible a proximite';
            return;
        }

        if (!state.streetViewInitialized) {
            new google.maps.StreetViewPanorama(streetContainer, {
                position: state.streetViewPosition,
                pov: { heading: 0, pitch: 0 },
                zoom: 1,
                addressControl: true,
                zoomControl: true,
                linksControl: true,
                fullscreenControl: false
            });
            state.streetViewInitialized = true;
            streetStatus.innerText = '';
        }
    }
}

function openStreetViewModal(uid) {
    const state = getState(uid);
    if (!state || !state.streetViewPosition) {
        return;
    }

    const modal = document.getElementById('streetViewModal');
    const title = document.getElementById('streetViewTitle');
    const container = document.getElementById('streetViewPanoramaModal');

    title.innerText = `${state.university.name} - Street View`;
    container.innerHTML = '';
    modal.classList.add('active');

    new google.maps.StreetViewPanorama(container, {
        position: state.streetViewPosition,
        pov: { heading: 0, pitch: 0 },
        zoom: 1,
        addressControl: true,
        zoomControl: true,
        linksControl: true,
        fullscreenControl: true
    });
}

function closeStreetViewModal() {
    const modal = document.getElementById('streetViewModal');
    modal.classList.remove('active');
}

document.getElementById('streetViewModal').addEventListener('click', (event) => {
    if (event.target.id === 'streetViewModal') {
        closeStreetViewModal();
    }
});

window.MobilityMapStreetView = {
    findPlaceByUniversity: window.findPlaceByUniversity,
    findStreetViewPosition: window.findStreetViewPosition,
    hydratePopupContent,
    switchPopupTab,
    openStreetViewModal,
    closeStreetViewModal,
};

window.hydratePopupContent = hydratePopupContent;
window.switchPopupTab = switchPopupTab;
window.openStreetViewModal = openStreetViewModal;
window.closeStreetViewModal = closeStreetViewModal;
