import {
    buildFiliereOptionsHtml,
    callbacks,
    editableUniversities,
    escapeHtml,
    filieresById,
    submittedWishesByStudent,
    universitiesById,
    wishesCountByUniversityId,
    wishesFilieresSet,
} from './state.js';
import { getDashboardRows } from './wishes_table.js';

export const fetchUniversityCatalog = async () => {
    let universities = [];
    try {
        const response = await fetch('/api.php?path=/university/admin/catalog');
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        const data = await response.json();
        if (data && data.universities && data.semesters) {
            universities = data.universities;
            window.MobilityMapState.semesters = data.semesters;
        } else {
            universities = Array.isArray(data) ? data : [];
            window.MobilityMapState.semesters = [
                { id: 4, label: 'S8' },
                { id: 5, label: 'S9' },
            ];
        }
    } catch (error) {
        console.error(error.message);
        window.MobilityMapState.semesters = [
            { id: 4, label: 'S8' },
            { id: 5, label: 'S9' },
        ];
    }

    return universities;
};

export const fetchWishes = async () => {
    let wishes = [];
    try {
        const response = await fetch('/api.php?path=/university/admin/wishes');
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        wishes = await response.json();
    } catch (error) {
        console.error(error.message);
    }

    return wishes;
};

export function hydrateCatalogState(universityCatalogRows) {
    universitiesById.clear();
    filieresById.clear();
    editableUniversities.splice(0, editableUniversities.length);

    for (const row of universityCatalogRows) {
        const uid = String(row.id_partner_university);
        if (!universitiesById.has(uid)) {
            universitiesById.set(uid, {
                ...row,
                filieres: [],
                filiereIds: new Set(),
                wishCount: 0,
            });
        }

        const university = universitiesById.get(uid);
        if (row.id_filiere !== null && row.id_filiere !== undefined) {
            const filiereId = String(row.id_filiere);
            university.filiereIds.add(filiereId);
            university.filieres.push({
                id_filiere: row.id_filiere,
                nom_filiere: row.nom_filiere,
                nom_long: row.nom_long,
                annee: row.annee,
                number_of_places: row.number_of_places,
            });

            if (!filieresById.has(filiereId)) {
                filieresById.set(filiereId, {
                    id_filiere: row.id_filiere,
                    nom_filiere: row.nom_filiere,
                    nom_long: row.nom_long,
                });
            }
        }
    }

    const universities = Array.from(universitiesById.values()).map((university) => ({
        ...university,
        filieres: university.filieres.sort((a, b) => String(a.nom_filiere).localeCompare(String(b.nom_filiere))),
    }));

    editableUniversities.push(
        ...universities.map((u) => ({
            ...u,
            rowKey: String(u.id_partner_university),
            filiereIds: new Set(u.filiereIds || []),
            filieres: (u.filieres || []).map((f) => ({ ...f })),
            isDraft: false,
        }))
    );

    const filiereSelect = document.getElementById('filiereSelect');
    filiereSelect.innerHTML = '<option value="toutes">Toutes</option>' + buildFiliereOptionsHtml();
}

export async function refreshWishesFromServer() {
    const wishes = await fetchWishes();
    submittedWishesByStudent.clear();
    wishesCountByUniversityId.clear();
    wishes.forEach((wish) => {
        const universityKey = String(wish.id_partner_university);
        wishesCountByUniversityId.set(universityKey, (wishesCountByUniversityId.get(universityKey) || 0) + 1);

        if (!submittedWishesByStudent.has(wish.id_etudiant)) {
            submittedWishesByStudent.set(wish.id_etudiant, {
                student: {
                    id_etudiant: wish.id_etudiant,
                    nom: wish.etudiant_nom,
                    prenom: wish.etudiant_prenom,
                    mail: wish.etudiant_mail,
                    submission_date: wish.submission_date,
                    assignment_status: wish.assignment_status,
                    id_assignment: wish.id_assignment,
                    filiere_nom: wish.filiere_nom,
                },
                wishes: [],
            });
            if (wish.filiere_nom) {
                wishesFilieresSet.add(wish.filiere_nom);
            } else {
                wishesFilieresSet.add('Non renseignée');
            }
        }
        if (wish.id_wish) {
            submittedWishesByStudent.get(wish.id_etudiant).wishes.push(wish);
        }

        const catalogUniversity = universitiesById.get(String(wish.id_partner_university));
        if (catalogUniversity && wish.id_wish) {
            catalogUniversity.wishCount = wishesCountByUniversityId.get(String(wish.id_partner_university)) || 0;
        }
    });

    const filiereFilter = document.getElementById('wishesFiliereFilter');
    if (filiereFilter) {
        const currentVal = filiereFilter.value;
        filiereFilter.innerHTML = '<option value="toutes">Toutes</option>' + Array.from(wishesFilieresSet).sort().map((f) => `<option value="${escapeHtml(f)}">${escapeHtml(f)}</option>`).join('');
        if (Array.from(wishesFilieresSet).includes(currentVal)) {
            filiereFilter.value = currentVal;
        }
    }
}

export function refreshKpis() {
    const rows = getDashboardRows();
    const submittedCount = rows.filter((row) => row.isSubmitted).length;
    const incompleteCount = rows.filter((row) => !row.isSubmitted).length;
    const recentCount = rows.filter((row) => row.isRecent && row.isSubmitted).length;
    const targetedUniversitiesCount = new Set(
        rows.flatMap((row) => row.wishes.map((wish) => String(wish.id_partner_university || '')))
            .filter(Boolean)
    ).size;

    document.getElementById('kpiStudents').innerText = String(submittedCount);
    document.getElementById('kpiIncomplete').innerText = String(incompleteCount);
    document.getElementById('kpiUniversities').innerText = String(targetedUniversitiesCount);
    document.getElementById('kpiRecent').innerText = String(recentCount);
}

export async function refreshAllData() {
    const catalogRows = await fetchUniversityCatalog();
    hydrateCatalogState(catalogRows);
    await refreshWishesFromServer();
    refreshKpis();
    if (callbacks.renderDashboardTable) callbacks.renderDashboardTable();
    if (callbacks.renderUniversitiesAdminTable) callbacks.renderUniversitiesAdminTable();
    if (callbacks.updateMap) callbacks.updateMap();
}

callbacks.refreshAllData = refreshAllData;
