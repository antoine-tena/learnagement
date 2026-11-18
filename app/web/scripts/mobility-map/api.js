export const fetchUniversities = async () => {
    let universities = [];
    try {
        const response = await fetch('/api.php?path=/university');
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        universities = await response.json();
        console.log('Universities: ', universities);
    } catch (error) {
        console.error(error.message);
    }

    return universities;
};

export const fetchWishes = async () => {
    let wishes = [];
    try {
        const response = await fetch('/api.php?path=/university/etudiant/' + window.ENV.USER_ID + '/wishes');
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        wishes = await response.json();
    } catch (error) {
        console.error(error.message);
    }

    return wishes;
};

export const fetchCampaignStatus = async () => {
    try {
        const statusRes = await fetch('/api.php?path=/university/etudiant/' + window.ENV.USER_ID + '/campaign-status');
        if (statusRes.ok) {
            const statusData = await statusRes.json();
            return statusData.is_open === true;
        }
    } catch (e) {
        console.error('Impossible de récupérer le statut de la campagne', e);
    }
    return false;
};

export const fetchAssignment = async () => {
    try {
        const response = await fetch('/api.php?path=/university/etudiant/' + window.ENV.USER_ID + '/assignment');
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.error(error.message);
    }
    return null;
};

export const fetchStudentQuota = async () => {
    try {
        const response = await fetch('/api.php?path=/university/etudiant/' + window.ENV.USER_ID + '/quota?annee_scolaire=2025-2026');
        if (response.ok) {
            const data = await response.json();
            if (data) {
                const container = document.getElementById('studentQuotaContainer');
                if (container) container.classList.remove('hidden');

                const filiereNameEl = document.getElementById('quotaFiliereName');
                if (filiereNameEl) filiereNameEl.innerText = data.filiere || 'Filière';

                const s8El = document.getElementById('quotaS8Count');
                if (s8El) s8El.innerText = data.S8 ?? 0;

                const s9El = document.getElementById('quotaS9Count');
                if (s9El) s9El.innerText = data.S9 ?? 0;
            }
        }
    } catch (e) {
        console.error('Erreur quota', e);
    }
};

export function escapeHtml(value) {
    return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
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
