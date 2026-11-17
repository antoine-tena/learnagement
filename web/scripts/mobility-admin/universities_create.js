import { buildFiliereOptionsHtml, callbacks } from './state.js';

export function addNewUniversityPlaceRow(annee, containerId) {
    const rowId = `new-place-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
    const rowHtml = `
        <div id="${rowId}" class="grid grid-cols-[2fr_1fr_auto] gap-2 items-center" data-annee="${annee}">
            <select class="new-uni-place-filiere border rounded px-2 py-1 text-xs">${buildFiliereOptionsHtml()}</select>
            <input type="number" min="0" value="1" class="new-uni-place-count border rounded px-2 py-1 text-xs" />
            <button type="button" class="text-xs px-2 py-1 rounded bg-red-50 text-red-700 hover:bg-red-100" onclick="document.getElementById('${rowId}').remove()">Supprimer</button>
        </div>
    `;
    document.getElementById(containerId).insertAdjacentHTML('beforeend', rowHtml);
}

export function resetAddUniversityForm() {
    document.getElementById('newUniName').value = '';
    document.getElementById('newUniCountry').value = '';
    document.getElementById('newUniCode').value = '';
    document.getElementById('newUniAddress').value = '';
    document.getElementById('newUniWebsite').value = '';
    document.getElementById('newUniLanguages').value = 'Anglais';
    document.getElementById('newUniLatitude').value = '48.85';
    document.getElementById('newUniLongitude').value = '2.35';
    document.getElementById('newUniNoteMin').value = '';
    document.getElementById('newUniType').value = 'ERASMUS';
    document.getElementById('newUniS8Total').value = '0';
    document.getElementById('newUniS9Total').value = '0';
    document.getElementById('newUniPlacesRowsS8').innerHTML = '';
    document.getElementById('newUniPlacesRowsS9').innerHTML = '';
    addNewUniversityPlaceRow(4, 'newUniPlacesRowsS8');
    addNewUniversityPlaceRow(5, 'newUniPlacesRowsS9');
}

export function collectNewUniversityPlaces() {
    const placeRows = Array.from(document.querySelectorAll('#newUniPlacesRowsS8 > div, #newUniPlacesRowsS9 > div'));
    return placeRows.map((row) => {
        const filiere = row.querySelector('.new-uni-place-filiere');
        const count = row.querySelector('.new-uni-place-count');
        const annee = row.getAttribute('data-annee');
        return {
            id_filiere: Number(filiere?.value || 0),
            annee: Number(annee || 4),
            number_of_places: Math.max(0, Number.parseInt(count?.value || '0', 10) || 0),
        };
    });
}

export async function saveNewUniversity() {
    const payload = {
        name: document.getElementById('newUniName').value.trim(),
        country: document.getElementById('newUniCountry').value.trim(),
        code: document.getElementById('newUniCode').value.trim() || null,
        address: document.getElementById('newUniAddress').value.trim() || null,
        website: document.getElementById('newUniWebsite').value.trim() || null,
        languages: document.getElementById('newUniLanguages').value.trim() || null,
        latitude: Number(document.getElementById('newUniLatitude').value || 0),
        longitude: Number(document.getElementById('newUniLongitude').value || 0),
        note_min: document.getElementById('newUniNoteMin').value === '' ? null : Number(document.getElementById('newUniNoteMin').value),
        type: document.getElementById('newUniType').value || 'ERASMUS',
        S8_total_places: Number(document.getElementById('newUniS8Total').value || 0),
        S9_total_places: Number(document.getElementById('newUniS9Total').value || 0),
        places: collectNewUniversityPlaces(),
    };

    if (!payload.name || !payload.country) {
        window.alert('Nom et pays sont obligatoires.');
        return;
    }

    const seen = new Set();
    for (const p of payload.places) {
        const key = `${p.id_filiere}-${p.annee}`;
        if (seen.has(key)) {
            window.alert(`Erreur : Une filière a été ajoutée plusieurs fois pour le semestre S${p.annee === 4 ? '8' : '9'}. Veuillez retirer les doublons.`);
            return;
        }
        seen.add(key);
    }

    const response = await fetch('/university/admin', {
        method: 'POST',
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
    }

    document.getElementById('addUniversityPanel').classList.add('hidden');
    if (callbacks.refreshAllData) await callbacks.refreshAllData();
    window.alert('Université créée avec succès !');
    resetAddUniversityForm();
}
