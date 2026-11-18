const activeFilters = {};
let myGantt = null;
let tagsContainer = null;
let ganttInitialized = false;
let allTasksData = null;

const FILTER_FIELD_MAP = {
    'filiere-filter': ['filiere'],
    'periode-filter': ['semester'],
    'module-filter':  ['name'],
};

console.log("token", token);
console.log("id utilisateur", userId);
console.log("Données pour le Gantt :", dataGantt);


function getNextSemestre(semestre) {
    if (!semestre) return "S1";
    const num = parseInt(semestre.replace('S', ''));
    return `S${num + 1}`;
}

function formatDate(dateObj) {
    const y = dateObj.getFullYear();
    const m = String(dateObj.getMonth() + 1).padStart(2, '0');
    const d = String(dateObj.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
}

// Vue Enseignant -> On regroupe tout sur une seule année académique (2024-2025)
function semesterToDateEnseignant(semestre) {
    if (!semestre) return { start: "2024-09-01", end: "2025-06-30" };
    const num = parseInt(semestre.replace('S', ''));

    if (num % 2 !== 0) {
        return { start: "2024-09-01", end: "2025-01-15" };
    }
    else {
        return { start: "2025-01-20", end: "2025-06-30" };
    }
}
function semesterToDateEtudiant(semestre) {
    const semestreMap = {
        "S1": { start: "2023-09-01", end: "2024-01-15" },
        "S2": { start: "2024-01-20", end: "2024-06-30" },
        "S3": { start: "2024-09-01", end: "2025-01-15" },
        "S4": { start: "2025-01-20", end: "2025-06-30" },
        "S5": { start: "2025-09-01", end: "2026-01-15" },
        "S6": { start: "2026-01-20", end: "2026-06-30" },
        "S7": { start: "2026-09-01", end: "2027-01-15" },
        "S8": { start: "2027-01-20", end: "2027-06-30" },
        "S9": { start: "2027-09-01", end: "2028-01-15" },
        "S10": { start: "2028-01-20", end: "2028-06-30" }
    };
    return semestreMap[semestre] || { start: "2024-01-01", end: "2024-06-01" };
}

function transformDataForDHTMLX(dataGantt, userType) {
    const tasksMap = new Map();
    const links = [];
    let linkIdCounter = 1;

    // Durée par défaut courte pour eviter que les blocs prennent tout le semestre
    const DEFAULT_DURATION_DAYS = 14;

    // Création des liens
    dataGantt.forEach(item => {
            const prvKey = `${item.prv_code_module}_${item.prv_type}`;
            const nxtKey = `${item.nxt_code_module}_${item.nxt_type}`;
        if (!tasksMap.has(prvKey)) {
            const dates = userType === 'enseignant'
                ? semesterToDateEnseignant(item.prv_semestre)
                : semesterToDateEtudiant(item.prv_semestre);

            tasksMap.set(prvKey, {
                id: prvKey,
                text: prvKey,
                name: item.prv_nom,
                start_date: dates.start,
                duration: item.prv_duree_h ? Math.ceil(item.prv_duree_h / 2) : DEFAULT_DURATION_DAYS,
                code_module: item.prv_code_module,
                duree_h: item.prv_duree_h,
                type: item.prv_type,
                semester: item.prv_semestre,
                filiere: item.prv_discipline
            });
        }

        // Enfant
        const nxtSemestre = item.nxt_semestre || getNextSemestre(item.prv_semestre);
        if (!tasksMap.has(nxtKey)) {
            const dates = userType === 'enseignant'
                ? semesterToDateEnseignant(nxtSemestre)
                : semesterToDateEtudiant(nxtSemestre);

            tasksMap.set(nxtKey, {
                id: nxtKey,
                text: nxtKey,
                name: item.nxt_nom,
                start_date: dates.start,
                duration: item.nxt_duree_h ? Math.ceil(item.nxt_duree_h / 2) : DEFAULT_DURATION_DAYS,
                code_module: item.nxt_code_module,
                duree_h: item.nxt_duree_h,
                type: item.nxt_type,
                semester: item.nxt_semestre,
                filiere: item.nxt_discipline
            });
        }

        if (prvKey !== nxtKey){
            links.push({
                id: linkIdCounter++,
                source: prvKey,
                target: nxtKey,
                type: "0"
            });
        }
    });

    // Auto-scheduling
    let hasChanged = true;
    let loopLimit = 100;

    while (hasChanged && loopLimit > 0) {
        hasChanged = false;
        loopLimit--;

        links.forEach(link => {
            const parent = tasksMap.get(link.source);
            const child = tasksMap.get(link.target);

            if (parent && child) {
                const parentStartDate = new Date(parent.start_date);
                const parentEndDate = new Date(parentStartDate);
                parentEndDate.setDate(parentEndDate.getDate() + parent.duration);

                const childStartDate = new Date(child.start_date);

                if (childStartDate < parentEndDate) {
                    child.start_date = formatDate(parentEndDate);
                    hasChanged = true;
                }
            }
        });
    }

    if (loopLimit === 0) {
        console.warn("Attention : Dépendance circulaire détectée dans les modules.");
    }

    return {
        data: Array.from(tasksMap.values()),
        links: links
    };
}
