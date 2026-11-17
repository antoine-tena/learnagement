import {
    callbacks,
    editableUniversities,
    escapeHtml,
    expandedUniversityRows,
    filieresById,
    wishesCountByUniversityId,
} from './state.js';

export function getEditableUniversityByKey(rowKey) {
    return editableUniversities.find((u) => String(u.rowKey) === String(rowKey));
}

export function renderUniversitiesAdminTable() {
    const body = document.getElementById('universitiesAdminBody');
    const query = (document.getElementById('universityAdminSearch').value || '').trim().toLowerCase();

    let rows = [...editableUniversities];
    if (query) {
        rows = rows.filter((u) => {
            const text = [u.name, u.country, u.code, u.website].join(' ').toLowerCase();
            return text.includes(query);
        });
    }

    rows.sort((a, b) => String(a.name || '').localeCompare(String(b.name || '')));

    if (rows.length === 0) {
        body.innerHTML = '<tr><td colspan="5" class="px-6 py-10 text-center text-gray-500">Aucune universite ne correspond a la recherche.</td></tr>';
        return;
    }

    body.innerHTML = rows.map((u) => {
        const key = String(u.rowKey);
        const isExpanded = expandedUniversityRows.has(key);
        const wishesCount = wishesCountByUniversityId.get(String(u.id_partner_university || '')) || 0;
        const s8Filieres = (u.filieres || []).filter((f) => Number(f.annee) === 4);
        const s9Filieres = (u.filieres || []).filter((f) => Number(f.annee) === 5);

        const renderFiliereRow = (f) => {
            const index = u.filieres.indexOf(f);
            const filiereText = f.nom_filiere || f.nom_long || `Filiere ${f.id_filiere}`;
            return `
                <div class="grid grid-cols-[2fr_1fr_auto] gap-2 items-center rounded border border-gray-200 bg-white p-2">
                    <div class="text-xs text-gray-700">${escapeHtml(filiereText)}</div>
                    <input type="number" min="0" value="${escapeHtml(String(f.number_of_places ?? 0))}" class="border rounded px-2 py-1 text-xs" onchange="window.updateUniversityPlace('${escapeHtml(key)}', ${index}, this.value)" />
                    <button type="button" class="text-xs px-2 py-1 rounded bg-red-50 text-red-700 hover:bg-red-100" onclick="window.removeUniversityPlace('${escapeHtml(key)}', ${index})">Supprimer</button>
                </div>
            `;
        };

        const filiereRowsS8 = s8Filieres.map(renderFiliereRow).join('');
        const filiereRowsS9 = s9Filieres.map(renderFiliereRow).join('');

        return `
            <tr class="hover:bg-gray-100 transition">
                <td class="px-6 py-4">
                    <div class="font-semibold text-gray-900">${escapeHtml(u.name || 'Nouvelle universite')}</div>
                </td>
                <td class="px-6 py-4 text-gray-600">${escapeHtml(u.country || '-')}</td>
                <td class="px-6 py-4 text-gray-600">${escapeHtml(u.code || '-')}</td>
                <td class="px-6 py-4 text-gray-900 font-semibold">${escapeHtml(String(wishesCount))}</td>
                <td class="px-6 py-4">
                    <div class="flex items-center justify-end gap-2">
                        <button type="button" class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg text-blue-700 bg-blue-50 hover:bg-blue-100 transition" onclick="window.toggleUniversityPlacesEditor('${escapeHtml(key)}')">Editer les places</button>
                    </div>
                </td>
            </tr>
            ${isExpanded ? `
            <tr class="bg-gray-50">
                <td colspan="5" class="px-6 py-4">
                    <div class="space-y-3">
                        <div class="grid grid-cols-1 lg:grid-cols-3 gap-2">
                            <input type="text" value="${escapeHtml(u.name || '')}" placeholder="Nom universite" class="border rounded px-2 py-1 text-xs" onchange="window.updateUniversityMeta('${escapeHtml(key)}', 'name', this.value)" />
                            <input type="text" value="${escapeHtml(u.country || '')}" placeholder="Pays" class="border rounded px-2 py-1 text-xs" onchange="window.updateUniversityMeta('${escapeHtml(key)}', 'country', this.value)" />
                            <input type="text" value="${escapeHtml(u.code || '')}" placeholder="Code" class="border rounded px-2 py-1 text-xs" onchange="window.updateUniversityMeta('${escapeHtml(key)}', 'code', this.value)" />
                        </div>

                        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-3">
                            <div class="rounded border bg-white p-3">
                                <h4 class="text-xs font-semibold uppercase tracking-wide text-gray-600 mb-2">Semestre 8 (S8)</h4>
                                <div class="mb-3">
                                    <label class="text-[10px] uppercase font-semibold text-gray-500 mb-1 block">Places globales S8</label>
                                    <input type="number" value="${escapeHtml(String(u.S8_total_places || 0))}" min="0" class="border rounded px-2 py-1 text-xs w-full" onchange="window.updateUniversityMeta('${escapeHtml(key)}', 'S8_total_places', Number(this.value))" />
                                </div>
                                <div class="flex flex-wrap items-center gap-2 mb-2">
                                    <select id="addPlaceFiliereS8-${escapeHtml(key)}" class="border rounded px-2 py-1 text-xs flex-1">
                                        ${Array.from(filieresById.values()).sort((a, b) => String(a.nom_filiere).localeCompare(String(b.nom_filiere))).map((f) => `<option value="${escapeHtml(String(f.id_filiere))}">${escapeHtml(f.nom_filiere || f.nom_long || 'Filiere')}</option>`).join('')}
                                    </select>
                                    <button type="button" class="text-xs px-2 py-1 rounded bg-gray-200 text-gray-700 hover:bg-gray-300" onclick="window.addUniversityPlace('${escapeHtml(key)}', 4)">Ajouter</button>
                                </div>
                                <div class="space-y-2">
                                    ${filiereRowsS8 || '<div class="text-xs text-gray-500">Aucune place configuree.</div>'}
                                </div>
                            </div>

                            <div class="rounded border bg-white p-3">
                                <h4 class="text-xs font-semibold uppercase tracking-wide text-gray-600 mb-2">Semestre 9 (S9)</h4>
                                <div class="mb-3">
                                    <label class="text-[10px] uppercase font-semibold text-gray-500 mb-1 block">Places globales S9</label>
                                    <input type="number" value="${escapeHtml(String(u.S9_total_places || 0))}" min="0" class="border rounded px-2 py-1 text-xs w-full" onchange="window.updateUniversityMeta('${escapeHtml(key)}', 'S9_total_places', Number(this.value))" />
                                </div>
                                <div class="flex flex-wrap items-center gap-2 mb-2">
                                    <select id="addPlaceFiliereS9-${escapeHtml(key)}" class="border rounded px-2 py-1 text-xs flex-1">
                                        ${Array.from(filieresById.values()).sort((a, b) => String(a.nom_filiere).localeCompare(String(b.nom_filiere))).map((f) => `<option value="${escapeHtml(String(f.id_filiere))}">${escapeHtml(f.nom_filiere || f.nom_long || 'Filiere')}</option>`).join('')}
                                    </select>
                                    <button type="button" class="text-xs px-2 py-1 rounded bg-gray-200 text-gray-700 hover:bg-gray-300" onclick="window.addUniversityPlace('${escapeHtml(key)}', 5)">Ajouter</button>
                                </div>
                                <div class="space-y-2">
                                    ${filiereRowsS9 || '<div class="text-xs text-gray-500">Aucune place configuree.</div>'}
                                </div>
                            </div>
                        </div>

                        <div class="flex items-center justify-end gap-2">
                            <button type="button" class="text-xs px-3 py-1.5 rounded bg-green-600 text-white hover:bg-green-700" onclick="window.saveUniversityDraft('${escapeHtml(key)}')">Enregistrer</button>
                        </div>
                    </div>
                </td>
            </tr>
            ` : ''}
        `;
    }).join('');
}

export function toggleUniversityPlacesEditor(rowKey) {
    const key = String(rowKey);
    if (expandedUniversityRows.has(key)) {
        expandedUniversityRows.delete(key);
    } else {
        expandedUniversityRows.add(key);
    }
    renderUniversitiesAdminTable();
}

export function updateUniversityMeta(rowKey, field, value) {
    const university = getEditableUniversityByKey(rowKey);
    if (!university) return;
    university[field] = value;
}

export function updateUniversityPlace(rowKey, placeIndex, value) {
    const university = getEditableUniversityByKey(rowKey);
    if (!university || !university.filieres[placeIndex]) return;
    const parsed = Number.parseInt(value, 10);
    university.filieres[placeIndex].number_of_places = Number.isNaN(parsed) ? 0 : Math.max(0, parsed);
    const firstPlace = university.filieres[0];
    if (firstPlace) {
        university.number_of_places = firstPlace.number_of_places;
        university.annee = firstPlace.annee;
    }
    if (callbacks.updateMap) callbacks.updateMap();
}

export function removeUniversityPlace(rowKey, placeIndex) {
    const university = getEditableUniversityByKey(rowKey);
    if (!university) return;
    university.filieres.splice(placeIndex, 1);
    university.filiereIds = new Set(university.filieres.map((f) => String(f.id_filiere)));
    renderUniversitiesAdminTable();
    if (callbacks.updateMap) callbacks.updateMap();
}

export function addUniversityPlace(rowKey, annee) {
    const university = getEditableUniversityByKey(rowKey);
    if (!university) return;
    const filiereSelectEl = document.getElementById(`addPlaceFiliereS${annee === 4 ? '8' : '9'}-${rowKey}`);
    if (!filiereSelectEl) return;

    const filiereId = String(filiereSelectEl.value);

    const alreadyExists = university.filieres.some((f) => String(f.id_filiere) === filiereId && Number(f.annee) === Number(annee));
    if (alreadyExists) {
        window.alert(`Cette filière a déjà été ajoutée pour le semestre S${annee === 4 ? '8' : '9'}.`);
        return;
    }

    const filiereMeta = filieresById.get(filiereId);

    university.filieres.push({
        id_filiere: Number.parseInt(filiereId, 10),
        nom_filiere: filiereMeta?.nom_filiere || 'Filiere',
        nom_long: filiereMeta?.nom_long || '',
        annee,
        number_of_places: 1,
    });
    university.filiereIds.add(filiereId);
    const firstPlace = university.filieres[0];
    if (firstPlace) {
        university.number_of_places = firstPlace.number_of_places;
        university.annee = firstPlace.annee;
    }

    renderUniversitiesAdminTable();
    if (callbacks.updateMap) callbacks.updateMap();
}

export async function saveUniversityDraft(rowKey) {
    const university = getEditableUniversityByKey(rowKey);
    if (!university) return;

    const payload = {
        name: String(university.name || '').trim(),
        country: String(university.country || '').trim(),
        code: university.code || null,
        address: university.address || null,
        latitude: Number(university.latitude || 0),
        longitude: Number(university.longitude || 0),
        website: university.website || null,
        languages: university.languages || null,
        note_min: university.note_min === null || university.note_min === undefined || university.note_min === ''
            ? null
            : Number(university.note_min),
        type: university.type || 'ERASMUS',
        S8_total_places: Number(university.S8_total_places || 0),
        S9_total_places: Number(university.S9_total_places || 0),
        places: (university.filieres || []).map((f) => ({
            id_filiere: Number(f.id_filiere),
            annee: Number(f.annee),
            number_of_places: Math.max(0, Number.parseInt(f.number_of_places ?? 0, 10) || 0),
        })),
    };

    if (!payload.name || !payload.country) {
        window.alert('Nom et pays sont obligatoires.');
        return;
    }

    const response = await fetch("/university/admin/${university.id_partner_university}", {
        method: 'PUT',
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
    }

    if (callbacks.refreshAllData) await callbacks.refreshAllData();
    window.alert('Université mise à jour avec succès !');
}

callbacks.renderUniversitiesAdminTable = renderUniversitiesAdminTable;
