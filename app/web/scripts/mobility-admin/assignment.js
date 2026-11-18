import { callbacks } from './state.js';

let assignmentPollInterval = null;
window.assignedStudentsList = [];
window.chartEtape3 = null;

function startAssignmentPolling() {
    if (assignmentPollInterval) clearInterval(assignmentPollInterval);

    assignmentPollInterval = setInterval(async () => {
        try {
            const response = await fetch('/api.php?path=/university/admin/assignment/status');
            if (!response.ok) {
                throw new Error(`Response status: ${response.status}`);
            }

            if (response.ok) {
                const status = await response.json();

                document.getElementById('assignmentProgressBar').style.width = `${status.progress}%`;
                document.getElementById('assignmentProgressPercent').innerText = `${status.progress}%`;
                document.getElementById('assignmentProgressText').innerText = status.step;

                if (status.error) {
                    clearInterval(assignmentPollInterval);
                    alert("Erreur dans l'algorithme : " + status.error);
                    resetAssignmentUI();
                } else if (status.progress >= 100 || !status.is_running) {
                    clearInterval(assignmentPollInterval);
                    setTimeout(() => {
                        document.getElementById('procedureModal').classList.add('hidden');
                        alert('Algorithme terminé ! (Affectations enregistrées)');
                        resetAssignmentUI();
                        if (callbacks.refreshAllData) callbacks.refreshAllData();
                    }, 500);
                }
            }
        } catch (e) {
            console.error('Polling error', e);
        }
    }, 500);
}

function resetAssignmentUI() {
    document.getElementById('assignmentActions').classList.remove('hidden');
    document.getElementById('assignmentProgressContainer').classList.add('hidden');
    document.getElementById('assignmentProgressBar').style.width = '0%';
    document.getElementById('assignmentProgressPercent').innerText = '0%';
    document.getElementById('assignmentProgressText').innerText = 'Démarrage...';
}

export async function runAssignmentExec() {
    const payload = {
        annee_eligible: 4, // Procédure exclusive aux 4ème année
        mobility_quotas: window.mobilityQuotas,
    };

    try {
        const response = await fetch('/university/admin/assignment/run', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        document.getElementById('assignmentActions').classList.add('hidden');
        document.getElementById('assignmentProgressContainer').classList.remove('hidden');

        startAssignmentPolling();
    } catch (error) {
        alert('Erreur de connexion.');
    }
}

export function runAssignmentUI() {
    window.requireConfirmation(
        "Vous êtes sur le point de lancer l'algorithme d'affectation automatique. Ceci écrase les affectations précédentes non validées.",
        runAssignmentExec
    );
}

export async function fetchAssignedStudents() {
    try {
        const response = await fetch('/api.php?path=/university/admin/mobility/assigned-students');
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        if (response.ok) {
            window.assignedStudentsList = await response.json();

            if (typeof Chart !== 'undefined') {
                renderEtape3Chart();
            }
        }
    } catch (error) {
        console.error('Erreur chargement des affectations', error);
    }
}

export async function updateAssignmentStatusExec(idAssignment, newStatus) {
    const actionStr = newStatus === 'accepted' ? 'accepter' : (newStatus === 'declined' ? 'refuser' : 'mettre en attente');
    if (!confirm(`Êtes-vous sûr de vouloir ${actionStr} cette affectation ?`)) {
        return;
    }

    try {
        const payload = {
            id_assignment: parseInt(idAssignment, 10),
            new_status: newStatus,
        };

        const response = await fetch('/university/admin/mobility/update-assignment-status', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        if (response.ok) {
            fetchAssignedStudents(); // Met à jour le graphe
            if (callbacks.refreshAllData) {
                callbacks.refreshAllData(); // Met à jour la liste des étudiants
            }
        } else {
            alert('Erreur lors de la mise à jour.');
        }
    } catch (error) {
        alert('Erreur de connexion.');
    }
}

export function renderEtape3Chart() {
    const ctx = document.getElementById('chartEtape3Status');
    if (!ctx) return;

    let countAcc = 0;
    let countPend = 0;
    let countDec = 0;
    window.assignedStudentsList.forEach((s) => {
        if (s.status === 'accepted') countAcc++;
        else if (s.status === 'declined') countDec++;
        else countPend++;
    });

    if (window.chartEtape3) {
        window.chartEtape3.destroy();
    }

    window.chartEtape3 = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Acceptés', 'En attente', 'Refusés'],
            datasets: [{
                data: [countAcc, countPend, countDec],
                backgroundColor: ['#22c55e', '#f59e0b', '#ef4444'],
                borderWidth: 1,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 10 } } },
            },
        },
        plugins: [{
            id: 'textInsideSlices',
            afterDraw(chart) {
                const chartCtx = chart.ctx;
                chart.data.datasets.forEach((dataset, i) => {
                    const meta = chart.getDatasetMeta(i);
                    meta.data.forEach((element, index) => {
                        const data = dataset.data[index];
                        if (data > 0) {
                            chartCtx.save();
                            const centerPoint = element.tooltipPosition();
                            chartCtx.fillStyle = '#ffffff';
                            chartCtx.font = 'bold 14px Arial';
                            chartCtx.textAlign = 'center';
                            chartCtx.textBaseline = 'middle';
                            chartCtx.shadowColor = 'rgba(0,0,0,0.5)';
                            chartCtx.shadowBlur = 4;
                            chartCtx.fillText(data, centerPoint.x, centerPoint.y);
                            chartCtx.restore();
                        }
                    });
                });
            },
        }],
    });
}

export function closeAssignmentPhase() {
    window.requireConfirmation(
        "Cette action va clôturer la phase d'acceptation. TOUTES les affectations actuellement 'en attente' seront définitivement passées à 'refusé'.",
        async function () {
            try {
                const response = await fetch('/university/admin/mobility/assignment/close', {
                    method: 'POST',
                });
                if (!response.ok) {
                    throw new Error(`Response status: ${response.status}`);
                }

                alert('Opération terminée avec succès. Toutes les affectations en attente ont été refusées.');

                if (callbacks.refreshAllData) {
                    callbacks.refreshAllData();
                }
            } catch (error) {
                console.error(error);
                alert('Erreur: ' + error.message);
            }
        }
    );
}
