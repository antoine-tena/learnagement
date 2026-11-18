import {
    callbacks,
    escapeHtml,
    expandedStudentRows,
    formatDateFR,
    submittedWishesByStudent,
    universitiesById,
} from './state.js';

export function getDashboardRows() {
    return Array.from(submittedWishesByStudent.values()).map((entry) => {
        const wishes = [...entry.wishes].sort((a, b) => (a.priority || 99) - (b.priority || 99));
        const submissionDate = entry.student.submission_date ? new Date(entry.student.submission_date) : null;
        const isSubmitted = Boolean(entry.student.submission_date) && entry.student.submission_date !== 'null' && entry.student.submission_date !== 'None';
        let status = 'incomplet';
        if (isSubmitted && wishes.length >= 1) {
            status = 'complet';
        } else if (wishes.length === 0) {
            status = 'retardataire';
        }

        return {
            studentId: entry.student.id_etudiant,
            fullname: `${entry.student.prenom || ''} ${entry.student.nom || ''}`.trim(),
            email: entry.student.mail || '',
            submissionDate,
            submissionDateText: formatDateFR(entry.student.submission_date),
            wishes,
            wishesCount: wishes.length,
            status,
            isSubmitted,
            assignmentStatus: entry.student.assignment_status,
            assignmentId: entry.student.id_assignment,
            filiere: entry.student.filiere_nom || 'Non renseignée',
        };
    });
}

export function statusBadge(status) {
    if (status === 'complet') {
        return { label: 'Complet', className: 'bg-green-100 text-green-700' };
    }
    if (status === 'retardataire') {
        return { label: 'Retardataire', className: 'bg-red-100 text-red-700' };
    }
    return { label: 'Incomplet', className: 'bg-yellow-100 text-yellow-700' };
}

export function assignmentBadge(status) {
    if (status === 'accepted') return { label: 'Accepté', className: 'bg-green-100 text-green-700' };
    if (status === 'declined') return { label: 'Refusé', className: 'bg-red-100 text-red-700' };
    if (status === 'pending') return { label: 'En attente', className: 'bg-yellow-100 text-yellow-700' };
    return { label: 'Non affecté', className: 'bg-gray-100 text-gray-500' };
}

export function toggleWishDetails(studentId) {
    const key = String(studentId);
    if (expandedStudentRows.has(key)) {
        expandedStudentRows.delete(key);
    } else {
        expandedStudentRows.add(key);
    }
    renderDashboardTable();
}

export function renderDashboardTable() {
    const body = document.getElementById('wishesTableBody');
    const query = (document.getElementById('wishesSearch').value || '').trim().toLowerCase();
    const statusFilter = document.getElementById('dossierStatusFilter').value;
    const assignmentStatusFilter = document.getElementById('assignmentStatusFilter') ? document.getElementById('assignmentStatusFilter').value : 'tous';
    const filiereFilter = document.getElementById('wishesFiliereFilter') ? document.getElementById('wishesFiliereFilter').value : 'toutes';

    let rows = getDashboardRows();

    if (filiereFilter !== 'toutes') {
        rows = rows.filter((row) => row.filiere === filiereFilter);
    }

    if (assignmentStatusFilter !== 'tous') {
        rows = rows.filter((row) => {
            const as = row.assignmentStatus || 'none';
            return as === assignmentStatusFilter;
        });
    }

    if (statusFilter !== 'tous') {
        rows = rows.filter((row) => row.status === statusFilter);
    }

    if (query) {
        rows = rows.filter((row) => {
            const searchable = [
                row.fullname,
                row.email,
                ...row.wishes.map((w) => {
                    const uid = String(w.id_partner_university || '');
                    const uni = universitiesById.get(uid);
                    return uni ? `${uni.name} ${uni.country || ''}` : (w.university_name || '');
                }),
            ].join(' ').toLowerCase();

            return searchable.includes(query);
        });
    }

    const countText = rows.length + ' resultat' + (rows.length > 1 ? 's' : '');
    document.getElementById('wishesResultsCount').innerText = countText;

    if (rows.length === 0) {
        body.innerHTML = '<tr><td colspan="8" class="px-6 py-12 text-center text-gray-500">Aucun dossier ne correspond aux filtres.</td></tr>';
        return;
    }

    const html = rows.map((row) => {
        const badge = statusBadge(row.status);
        const assignBadge = assignmentBadge(row.assignmentStatus);
        const studentRowKey = String(row.studentId || '');
        const isExpanded = expandedStudentRows.has(studentRowKey);
        const initials = row.fullname
            .split(' ')
            .filter(Boolean)
            .map((word) => word[0].toUpperCase())
            .join('')
            .slice(0, 3);
        const wishRows = row.wishes.slice(0, 5).map((wish, index) => {
            const wishId = String(wish.id_partner_university || '');
            const uni = universitiesById.get(wishId);
            const wishName = uni ? uni.name : (wish.university_name || `Universite ${wishId}`);
            const wishCountry = uni ? uni.country : (wish.university_country || '');
            const wishCode = uni ? uni.code : (wish.university_code || '');
            const semesterPrefix = wish.id_semestre ? `[S${wish.id_semestre}] ` : '';

            return `
                <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 rounded-lg border border-gray-200 bg-white p-3">
                    <div class="min-w-0">
                        <div class="text-sm font-semibold text-gray-900">#${index + 1} - ${semesterPrefix}${escapeHtml(wishName)}</div>
                        <div class="text-xs text-gray-500">${escapeHtml(wishCountry)} - ${escapeHtml(wishCode || '')}</div>
                    </div>
                    <button type="button" class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg text-blue-700 bg-blue-50 hover:bg-blue-100 transition shrink-0" onclick="window.scrollToUniversityOnMap('${escapeHtml(wishId)}')">Voir sur la carte</button>
                </div>
            `;
        }).join('');

        return `
            <tr class="hover:bg-gray-100 transition">
                <td class="px-6 py-4">
                    <div class="flex items-center gap-3">
                        <div class="w-9 h-9 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
                            <span class="text-xs font-bold text-blue-600">${escapeHtml(initials || 'NA')}</span>
                        </div>
                        <div>
                            <div class="font-semibold text-gray-900">${escapeHtml(row.fullname || 'Etudiant')}</div>
                            <div class="text-xs text-gray-500">${escapeHtml(row.email || '-')}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-gray-700">${escapeHtml(row.studentId || '-')}</td>
                <td class="px-6 py-4 whitespace-nowrap text-gray-700 font-medium">${escapeHtml(row.filiere || '-')}</td>
                <td class="px-6 py-4 whitespace-nowrap text-gray-600">${escapeHtml(row.submissionDateText)}</td>
                <td class="px-6 py-4">
                    <div class="flex items-center gap-2">
                        <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${badge.className}">${badge.label}</span>
                        ${row.isSubmitted ? `<button type="button" class="inline-flex items-center justify-center px-2 py-1 bg-red-50 text-red-600 hover:bg-red-100 hover:text-red-700 border border-red-200 rounded text-xs font-semibold transition shadow-sm" onclick="window.resetStudentWishes('${escapeHtml(row.studentId)}')" title="Annuler la soumission">Annuler</button>` : ''}
                    </div>
                </td>
                <td class="px-6 py-4 text-gray-900 font-semibold">${row.wishesCount}/5</td>
                <td class="px-6 py-4">
                    <div class="flex items-center gap-2">
                        <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${assignBadge.className}">${assignBadge.label}</span>
                        ${row.assignmentId ? `
                            <select class="text-xs border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500 bg-gray-50 py-1" onchange="if(this.value) window.updateAssignmentStatusExec('${escapeHtml(row.assignmentId)}', this.value); this.value=''">
                                <option value="" disabled selected>Modifier</option>
                                <option value="accepted">Accepter</option>
                                <option value="declined">Refuser</option>
                                <option value="pending">En attente</option>
                            </select>
                        ` : ''}
                    </div>
                </td>
                <td class="px-6 py-4">
                    <div class="flex items-center justify-end gap-2">
                        <button type="button" class="inline-flex items-center justify-center w-8 h-8 rounded-full border border-gray-300 text-gray-600 hover:bg-gray-100 transition" onclick="window.toggleWishDetails('${escapeHtml(studentRowKey)}')" aria-label="Afficher les voeux">
                            <svg class="w-4 h-4 transition ${isExpanded ? 'rotate-180' : ''}" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
                        </button>
                    </div>
                </td>
            </tr>
            ${isExpanded ? `
            <tr class="bg-gray-50">
                <td colspan="8" class="px-6 py-4">
                    <div class="space-y-2">
                        ${wishRows || '<div class="text-sm text-gray-500">Aucun voeu enregistre.</div>'}
                    </div>
                </td>
            </tr>
            ` : ''}
        `;
    }).join('');

    body.innerHTML = html;
}

export function toggleWishesModal() {
    const modal = document.getElementById('wishesModal');
    modal.classList.toggle('hidden');
}

callbacks.renderDashboardTable = renderDashboardTable;
