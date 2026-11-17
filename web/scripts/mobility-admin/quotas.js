window.mobilityQuotas = [];
window.globalFilieres = [];

export async function fetchMobilityQuotas() {
    try {
        const response = await fetch('/university/admin/mobility-quotas?annee_scolaire=2025-2026', {
            method: 'GET',
        });
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        if (response.ok) {
            window.mobilityQuotas = await response.json();
            renderMobilityQuotas();
        }
    } catch (e) {
        console.error('Erreur chargement quotas', e);
    }
}

export async function saveMobilityQuotas() {
    const newQuotas = [];
    const inputsS8 = document.querySelectorAll('.quota-input-s8');
    const inputsS9 = document.querySelectorAll('.quota-input-s9');

    inputsS8.forEach((input) => {
        const places = parseInt(input.value, 10);
        if (!isNaN(places) && places > 0) {
            newQuotas.push({ id_filiere: parseInt(input.dataset.filiere, 10), id_semestre: 8, places });
        }
    });

    inputsS9.forEach((input) => {
        const places = parseInt(input.value, 10);
        if (!isNaN(places) && places > 0) {
            newQuotas.push({ id_filiere: parseInt(input.dataset.filiere, 10), id_semestre: 9, places });
        }
    });

    window.mobilityQuotas = newQuotas;

    try {
        const response = await fetch('/university/admin/mobility-quotas', {
            method: 'POST',
            body: JSON.stringify({ annee_scolaire: '2025-2026', quotas: window.mobilityQuotas }),
        });
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        if (response.ok) {
            alert('Quotas sauvegardés avec succès !');
            document.getElementById('quotasModal').classList.add('hidden');
        } else {
            alert('Erreur lors de la sauvegarde des quotas.');
        }
    } catch (e) {
        console.error('Erreur sauvegarde quotas', e);
    }
}

export async function fetchGlobalFilieres() {
    try {
        const response = await fetch('/api.php?path=/filieres');
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        if (response.ok) {
            window.globalFilieres = await response.json();
        }
    } catch (e) {
        console.error('Erreur chargement filières', e);
    }
}

export function renderMobilityQuotas() {
    const tbody = document.getElementById('quotasGridBody');
    if (!tbody || !window.globalFilieres) return;

    if (window.globalFilieres.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="px-4 py-8 text-center text-gray-400 italic">Aucune filière trouvée.</td></tr>';
        return;
    }

    const sortedFilieres = [...window.globalFilieres].sort((a, b) => String(a.nom_filiere).localeCompare(String(b.nom_filiere)));

    let html = '';
    sortedFilieres.forEach((f) => {
        const nom = f.nom_filiere || f.nom_long || `Filière ${f.id_filiere}`;

        const qS8 = window.mobilityQuotas.find((q) => q.id_filiere === f.id_filiere && q.id_semestre === 8);
        const qS9 = window.mobilityQuotas.find((q) => q.id_filiere === f.id_filiere && q.id_semestre === 9);

        const placesS8 = qS8 ? qS8.places : 0;
        const placesS9 = qS9 ? qS9.places : 0;

        html += `
            <tr class="hover:bg-gray-50 transition">
                <td class="px-4 py-3 font-semibold text-gray-800">${nom}</td>
                <td class="px-4 py-3 text-center">
                    <input type="number" min="0" class="quota-input-s8 w-20 text-center text-sm border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500" data-filiere="${f.id_filiere}" value="${placesS8}">
                </td>
                <td class="px-4 py-3 text-center">
                    <input type="number" min="0" class="quota-input-s9 w-20 text-center text-sm border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500" data-filiere="${f.id_filiere}" value="${placesS9}">
                </td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

export async function saveQuotas() {
    // Implementation logic for saving quotas
}

export async function loadQuotas() {
    // Implementation logic for loading quotas
}
