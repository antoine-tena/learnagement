import { callbacks } from './state.js';

window.submittedStudentsList = [];
window.doublantsArray = [];

export async function forceSubmitWishesExec() {
    if (!confirm('Êtes-vous sûr de vouloir forcer la clôture de tous les dossiers de vœux incomplets ?\n\nTous les étudiants ayant fait au moins 1 choix verront leur dossier verrouillé et soumis.')) return;

    try {
        const response = await fetch('/university/admin/wishes/force-submit', {
            method: 'POST',
        });
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        alert('Tous les vœux incomplets ont été clôturés avec succès.');
        if (callbacks.refreshAllData) callbacks.refreshAllData();
    } catch (error) {
        alert('Erreur de connexion.');
    }
}

export function forceSubmitWishesUI() {
    window.requireConfirmation(
        'Vous êtes sur le point de clôturer définitivement toutes les soumissions de vœux. Tous les étudiants ayant fait au moins 1 choix verront leur dossier verrouillé.',
        forceSubmitWishesExec
    );
}

export async function fetchSubmittedStudents() {
    try {
        const response = await fetch('/api.php?path=/university/admin/mobility/submitted-students');
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        if (response.ok) {
            window.submittedStudentsList = await response.json();

            const filieres = [...new Set(window.submittedStudentsList.map((s) => s.nom_filiere))].filter(Boolean).sort();
            const container = document.getElementById('filiereQuotasContainer');
            if (container) {
                if (filieres.length > 0) {
                    container.innerHTML = '';
                    filieres.forEach((filiere) => {
                        const idSafe = 'quota_' + filiere.replace(/[^a-zA-Z0-9]/g, '_');
                        container.innerHTML += `
                            <div class="bg-white border border-gray-200 rounded p-2 flex flex-col justify-between">
                                <label for="${idSafe}" class="text-xs font-semibold text-gray-700 mb-1 truncate" title="${filiere}">${filiere}</label>
                                <input type="number" id="${idSafe}" data-filiere="${filiere}" class="filiere-quota-input w-full text-sm border-gray-300 rounded px-2 py-1" value="0" min="0">
                            </div>
                        `;
                    });
                } else {
                    container.innerHTML = '<span class="text-xs text-gray-400 italic">Aucune filière trouvée.</span>';
                }
            }
        }
    } catch (error) {
        console.error('Erreur chargement des étudiants soumis', error);
    }
}

export async function addDoublantToList() {
    const idInput = document.getElementById('doublantEtudiantId');
    const scoreInput = document.getElementById('doublantZScore');
    const id = parseInt(idInput.value);
    const score = parseFloat(scoreInput.value);

    if (!id || isNaN(score)) {
        alert('Veuillez renseigner un ID et un score valide.');
        return;
    }

    try {
        const response = await fetch('/api.php?path=/university/admin/campaign/doublant');
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        const student = await response.json();

        const existingIdx = window.doublantsArray.findIndex((d) => d.id_etudiant === id);
        if (existingIdx !== -1) {
            window.doublantsArray[existingIdx].z_score = score;
        } else {
            window.doublantsArray.push({
                id_etudiant: id,
                z_score: score,
                nom: student.nom,
                prenom: student.prenom,
                filiere: student.nom_filiere,
            });
        }

        idInput.value = '';
        scoreInput.value = '';
        renderDoublantsList();
    } catch (error) {
        console.error('Erreur vérification doublant', error);
        alert("Erreur lors de la vérification de l'étudiant.");
    }
}

export function removeDoublant(id) {
    window.doublantsArray = window.doublantsArray.filter((d) => d.id_etudiant !== id);
    renderDoublantsList();
}

export function renderDoublantsList() {
    const ul = document.getElementById('doublantsList');
    const header = document.getElementById('doublantsHeader');
    const countSpan = document.getElementById('doublantsCount');
    const filiereCounters = document.getElementById('doublantsFiliereCounters');

    if (window.doublantsArray.length > 0) {
        header.classList.remove('hidden');
        countSpan.textContent = window.doublantsArray.length + (window.doublantsArray.length > 1 ? ' Total' : ' Total');

        const filieresCount = {};
        window.doublantsArray.forEach((d) => {
            filieresCount[d.filiere] = (filieresCount[d.filiere] || 0) + 1;
        });

        const colors = [
            { bg: 'bg-indigo-50', text: 'text-indigo-800', border: 'border-indigo-200', badge: 'bg-indigo-100 text-indigo-800 border-indigo-200' },
            { bg: 'bg-emerald-50', text: 'text-emerald-800', border: 'border-emerald-200', badge: 'bg-emerald-100 text-emerald-800 border-emerald-200' },
            { bg: 'bg-amber-50', text: 'text-amber-800', border: 'border-amber-200', badge: 'bg-amber-100 text-amber-800 border-amber-200' },
            { bg: 'bg-rose-50', text: 'text-rose-800', border: 'border-rose-200', badge: 'bg-rose-100 text-rose-800 border-rose-200' },
            { bg: 'bg-fuchsia-50', text: 'text-fuchsia-800', border: 'border-fuchsia-200', badge: 'bg-fuchsia-100 text-fuchsia-800 border-fuchsia-200' },
            { bg: 'bg-cyan-50', text: 'text-cyan-800', border: 'border-cyan-200', badge: 'bg-cyan-100 text-cyan-800 border-cyan-200' },
        ];

        const filiereColorsMap = {};
        let colorIndex = 0;
        const getFiliereColor = (filiereName) => {
            if (!filiereName) return colors[0];
            if (!filiereColorsMap[filiereName]) {
                filiereColorsMap[filiereName] = colors[colorIndex % colors.length];
                colorIndex++;
            }
            return filiereColorsMap[filiereName];
        };

        filiereCounters.innerHTML = Object.entries(filieresCount).map(([filiere, count]) => {
            const c = getFiliereColor(filiere);
            return `<span class="${c.badge} text-xs font-bold px-2.5 py-1 rounded shadow-sm border">${filiere || 'N/A'}: ${count}</span>`;
        }).join('');

        ul.innerHTML = window.doublantsArray.map((d) => {
            const c = getFiliereColor(d.filiere);
            return `
            <li class="flex items-center justify-between gap-2 p-2.5 rounded-lg border ${c.bg} ${c.border} shadow-sm transition-all hover:shadow-md">
                <div class="flex-1 min-w-0">
                    <div class="text-xs font-bold text-gray-800 truncate" title="${d.nom} ${d.prenom}">${d.nom} ${d.prenom}</div>
                    <div class="text-[10px] text-gray-600 mt-0.5 flex items-center gap-1.5">
                        <span class="bg-white px-1 py-0.5 rounded font-medium border border-gray-200">ID: ${d.id_etudiant}</span>
                        <span class="truncate font-bold text-xs ${c.text}">${d.filiere}</span>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <div class="text-right">
                        <div class="text-[8px] uppercase font-bold text-gray-400 tracking-wider mb-0.5" title="Moyenne Centrée Réduite">MCR</div>
                        <div class="text-[11px] font-bold text-blue-700 bg-blue-50 border border-blue-100 px-1.5 py-0.5 rounded">${parseFloat(d.z_score).toFixed(2)}</div>
                    </div>
                    <button type="button" onclick="window.removeDoublant(${d.id_etudiant})" class="flex-shrink-0 w-6 h-6 rounded-full bg-red-50 text-red-500 hover:bg-red-500 hover:text-white flex items-center justify-center transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-1" title="Retirer cet étudiant">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"></path></svg>
                    </button>
                </div>
            </li>`;
        }).join('');
    } else {
        header.classList.add('hidden');
        ul.innerHTML = '';
    }
}

export async function launchCampaignExec() {
    try {
        document.getElementById('campaignLaunchControls').classList.add('hidden');
        const progressContainer = document.getElementById('campaignProgressContainer');
        const progressBar = document.getElementById('campaignProgressBar');
        const progressPercent = document.getElementById('campaignProgressPercent');
        const progressText = document.getElementById('campaignProgressText');

        progressContainer.classList.remove('hidden');
        progressBar.style.width = '0%';
        progressPercent.textContent = '0%';
        progressText.textContent = 'Nettoyage et initialisation...';

        let currentProgress = 0;
        const simulateProgress = setInterval(() => {
            if (currentProgress < 90) {
                currentProgress += Math.random() * 15;
                if (currentProgress > 90) currentProgress = 90;
                progressBar.style.width = currentProgress + '%';
                progressPercent.textContent = Math.floor(currentProgress) + '%';

                if (currentProgress > 30 && currentProgress < 60) {
                    progressText.textContent = 'Calcul des Z-scores en cours...';
                } else if (currentProgress >= 60) {
                    progressText.textContent = 'Sauvegarde des données...';
                }
            }
        }, 500);

        const response = await fetch('/university/admin/campaign/launch', {
            method: 'POST',
            body: JSON.stringify({ doublants: window.doublantsArray }),
        });
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        clearInterval(simulateProgress);
        progressBar.style.width = '100%';
        progressPercent.textContent = '100%';
        progressText.textContent = 'Campagne lancée avec succès !';

        if (response.ok) {
            setTimeout(() => {
                alert('Campagne lancée et scores calculés avec succès !');
                window.doublantsArray = [];
                renderDoublantsList();
                progressContainer.classList.add('hidden');
                document.getElementById('campaignLaunchControls').classList.remove('hidden');
                if (callbacks.refreshAllData) {
                    callbacks.refreshAllData();
                }
            }, 500);
        } else {
            const err = await response.json();
            alert('Erreur: ' + (err.detail || 'Impossible de lancer la campagne'));
            progressContainer.classList.add('hidden');
            document.getElementById('campaignLaunchControls').classList.remove('hidden');
        }
    } catch (e) {
        console.error('Erreur lancement campagne', e);
        alert('Erreur lors du lancement de la campagne.');
        document.getElementById('campaignProgressContainer').classList.add('hidden');
        document.getElementById('campaignLaunchControls').classList.remove('hidden');
    }
}

export function launchCampaign() {
    window.requireConfirmation(
        'Êtes-vous sûr de vouloir lancer la campagne ? Cela calculera les Moyennes Centrées Réduites de tous les étudiants de 4ème/5ème année et écrasera les affectations/vœux des doublants ajoutés.',
        launchCampaignExec
    );
}

export async function resetStudentWishes(idParam) {
    const id = typeof idParam === 'string' || typeof idParam === 'number' ? idParam : null;
    if (!id) return;

    if (!confirm("Êtes-vous sûr de vouloir annuler la soumission de cet étudiant ? Il repassera en statut 'En cours'.")) {
        return;
    }

    try {
        const response = await fetch('/university/admin/mobility/reset-wishes/' + id, {
            method: 'POST',
        });
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        if (response.ok) {
            alert('Soumission annulée avec succès.');
            fetchSubmittedStudents();
            if (callbacks.refreshAllData) {
                callbacks.refreshAllData();
            }
        } else {
            alert("Erreur lors de l'annulation.");
        }
    } catch (error) {
        alert('Erreur de connexion.');
    }
}
