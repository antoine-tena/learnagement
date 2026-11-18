export const expandedStudentRows = new Set();
export const expandedUniversityRows = new Set();
export const popupState = new Map();
export const wishesCountByUniversityId = new Map();
export const submittedWishesByStudent = new Map();
export const wishesFilieresSet = new Set();
export const universitiesById = new Map();
export const filieresById = new Map();
export const editableUniversities = [];

window.MobilityMapState = {
    popupState,
    submittedWishesByStudent,
    semesters: [],
    universitiesById,
    filieresById,
};

export const callbacks = {
    refreshAllData: null,
    renderDashboardTable: null,
    renderUniversitiesAdminTable: null,
    updateMap: null,
};

export function formatDateFR(dateValue) {
    if (!dateValue) return 'Non renseignee';
    const parsed = new Date(dateValue);
    if (Number.isNaN(parsed.getTime())) return 'Non renseignee';
    return parsed.toLocaleString('fr-FR');
}

export function escapeHtml(value) {
    return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

export function getSemesterLabel(annee) {
    return Number(annee) === 4 ? 'S8' : 'S9';
}

export function buildFiliereOptionsHtml() {
    return Array.from(filieresById.values())
        .sort((a, b) => String(a.nom_filiere).localeCompare(String(b.nom_filiere)))
        .map((filiere) => `<option value="${escapeHtml(String(filiere.id_filiere))}">${escapeHtml(filiere.nom_filiere || filiere.nom_long || 'Filiere')}</option>`)
        .join('');
}

export function buildSemestreOptionsHtml() {
    const semesters = window.MobilityMapState.semesters || [
        { id: 4, label: 'S8' },
        { id: 5, label: 'S9' },
    ];
    return semesters
        .map((sem) => `<option value="${escapeHtml(String(sem.id))}">${escapeHtml(sem.label || `S${sem.id}`)}</option>`)
        .join('');
}

export async function parseApiError(response) {
    try {
        const data = await response.json();
        return data?.detail || `Erreur ${response.status}`;
    } catch {
        return `Erreur ${response.status}`;
    }
}

export function getLanguageFlags(languagesString) {
    if (!languagesString) return '';
    const flags = {
        Allemand: '🇩🇪',
        Anglais: '🇬🇧',
        Espagnol: '🇪🇸',
        Français: '🇫🇷',
        Portugais: '🇵🇹',
        Italien: '🇮🇹',
        Japonais: '🇯🇵',
    };

    return languagesString.split(',').map((l) => {
        const lang = l.trim();
        return flags[lang] ? `<span title="${escapeHtml(lang)}" class="text-base cursor-help">${flags[lang]}</span>` : escapeHtml(lang);
    }).join(' ');
}
