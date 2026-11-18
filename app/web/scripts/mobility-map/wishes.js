import { escapeHtml, fetchWishes } from './api.js';

export const wishedUniversities = new Map();

export async function refreshWishesFromServer() {
    const wishes = await fetchWishes();
    wishedUniversities.clear();
    wishes.forEach((wish) => {
        wishedUniversities.set(`${wish.id_partner_university}-${wish.id_semestre}`, wish);
    });
}

export function renderWishesList() {
    const wishesList = document.getElementById('wishesList');
    const wishesEmpty = document.getElementById('wishesEmpty');
    const wishesCount = document.getElementById('wishesCount');
    const wishes = Array.from(wishedUniversities.values())
        .sort((a, b) => (a.priority ?? 999) - (b.priority ?? 999));

    wishesCount.innerText = String(wishes.length) + '/5';

    if (wishes.length === 0) {
        wishesList.innerHTML = '';
        if (window.MobilityMapState.campaignOpen !== false) {
            wishesEmpty.classList.remove('hidden');
        }
        return;
    }

    wishesEmpty.classList.add('hidden');

    const isSubmitted = wishes.some((w) => Boolean(w.submission_date) && w.submission_date !== 'null' && w.submission_date !== 'None');

    const campaignOpenBadge = document.getElementById('campaignOpenBadge');
    const wishesSubmittedBadge = document.getElementById('wishesSubmittedBadge');

    if (window.MobilityMapState.campaignOpen !== false) {
        if (isSubmitted) {
            if (campaignOpenBadge) campaignOpenBadge.classList.add('hidden');
            if (wishesSubmittedBadge) wishesSubmittedBadge.classList.remove('hidden');
        } else {
            if (campaignOpenBadge) campaignOpenBadge.classList.remove('hidden');
            if (wishesSubmittedBadge) wishesSubmittedBadge.classList.add('hidden');
        }
    }

    wishesList.innerHTML = wishes
        .map((wish, index) => `
        <li class="rounded border border-gray-200 bg-gray-50 p-2">
            <div class="flex items-center gap-4 mb-1">
                <span class="font-semibold text-lg text-gray-800">${index + 1}</span>
                <div class="flex items-center justify-between gap-2 w-full">
                    <div class="cursor-pointer flex-1 hover:text-primary transition-colors" onclick="window.flyToUniversity('${wish.id_partner_university}')" title="Voir sur la carte">
                        <p class="text-sm text-gray-800"><strong class="font-semibold">[S${escapeHtml(wish.id_semestre)}] ${escapeHtml(wish.name)}</strong> (${escapeHtml(wish.code)})</p>
                        <p class="text-xs text-gray-600">${escapeHtml(wish.country)}</p>
                    </div>
                    <div class="flex items-center gap-1 ${isSubmitted ? 'hidden' : ''}">
                        <button
                            type="button"
                            onclick="window.moveWish(${wish.id_partner_university}, ${wish.id_semestre}, 'up')"
                            ${(index === 0) ? 'disabled' : ''}
                            class="p-1 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-700 disabled:opacity-30 disabled:hover:bg-transparent transition"
                            title="Monter le voeu"
                        >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"></path></svg>
                        </button>
                        <button
                            type="button"
                            onclick="window.moveWish(${wish.id_partner_university}, ${wish.id_semestre}, 'down')"
                            ${(index === wishes.length - 1) ? 'disabled' : ''}
                            class="p-1 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-700 disabled:opacity-30 disabled:hover:bg-transparent transition"
                            title="Descendre le voeu"
                        >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>
                        </button>
                        <button
                            type="button"
                            onclick="window.deleteWish(${wish.id_partner_university}, ${wish.id_semestre})"
                            class="p-1 rounded hover:bg-red-50 text-gray-400 hover:text-red-500 transition ml-1"
                            title="Supprimer le voeu"
                        >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                        </button>
                    </div>
                </div>
            </div>
        </li>
        `)
        .join('');

    wishesList.innerHTML += `
        <button
            type="button"
            onclick="window.submitWishes()"
            class="mt-3 w-full rounded bg-primary px-3 py-2 text-sm font-semibold text-white cursor-pointer disabled:cursor-not-allowed disabled:bg-gray-400"
            ${wishes.length < 1 || isSubmitted ? 'disabled' : ''}
        >
            ${isSubmitted ? 'Voeux soumis' : 'Soumettre mes voeux'}
        </button>
    `;
}

export async function addUniversityToWishes(universityId, idSemestre) {
    const university = window.MobilityMapState.universitiesById.get(String(universityId));
    if (!university) {
        console.error('Universite introuvable pour id:', universityId);
        return;
    }

    if (wishedUniversities.has(`${university.id_partner_university}-${idSemestre}`)) {
        return;
    }

    try {
        const wishesEndpoint = '/api.php?path=/university/etudiant/' + window.ENV.USER_ID + '/wish/' + university.id_partner_university;

        const response = await fetch(wishesEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ id_semestre: idSemestre }),
        });

        if (!response.ok && response.status !== 409) {
            throw new Error(`Response status: ${response.status}`);
        }

        await refreshWishesFromServer();
        renderWishesList();
        window.updateMap();
        document.getElementById('wishesPanel').classList.remove('hidden');
    } catch (error) {
        console.error("Impossible d'ajouter l'université aux voeux :", error.message);
    }
}

export async function deleteWish(idPartnerUniversity, idSemestre) {
    try {
        const deleteEndpoint = '/api.php?path=/university/etudiant/' + window.ENV.USER_ID
            + '/wish/' + idPartnerUniversity
            + '/semestre/' + idSemestre;
        const response = await fetch(deleteEndpoint, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        await refreshWishesFromServer();
        renderWishesList();
        window.updateMap();
    } catch (error) {
        console.error('Impossible de supprimer le voeu :', error.message);
    }
}

export async function moveWish(idPartnerUniversity, idSemestre, direction) {
    try {
        const moveEndpoint = '/api.php?path=/university/etudiant/' + window.ENV.USER_ID
            + '/wish/' + idPartnerUniversity
            + '/semestre/' + idSemestre
            + '/move/' + direction;
        const response = await fetch(moveEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        await refreshWishesFromServer();
        renderWishesList();
        window.updateMap();
    } catch (error) {
        console.error('Impossible de deplacer le voeu :', error.message);
    }
}

export async function submitWishes() {
    if (!confirm('Êtes-vous sûr de vouloir soumettre vos voeux ? Cette action est définitive et vous ne pourrez plus les modifier par la suite.')) {
        return;
    }

    try {
        const submitEndpoint = '/api.php?path=/university/etudiant/' + window.ENV.USER_ID + '/wishes/submit';

        const response = await fetch(submitEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        alert('Voeux soumis avec succès !');
        await refreshWishesFromServer();
        renderWishesList();
        window.updateMap();
    } catch (error) {
        console.error('Impossible de soumettre les voeux :', error.message);
        alert('Erreur lors de la soumission des voeux.');
    }
}

export async function submitDecision(decision) {
    if (!confirm(`Êtes-vous sûr de vouloir ${decision === 'accepted' ? 'accepter' : 'refuser'} cette affectation ? Cette décision est définitive.`)) {
        return;
    }

    try {
        const endpoint = '/api.php?path=/university/etudiant/' + window.ENV.USER_ID + '/assignment/decision';

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ decision }),
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Erreur inconnue');
        }

        window.MobilityMapState.assignment.status = decision;

        window.updateMap();
        setTimeout(() => {
            window.flyToUniversity(window.MobilityMapState.assignment.id_partner_university);
        }, 100);
    } catch (error) {
        console.error('Erreur lors de la décision :', error.message);
        alert('Une erreur est survenue : ' + error.message);
    }
}
