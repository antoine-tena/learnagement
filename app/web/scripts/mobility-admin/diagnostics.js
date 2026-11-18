let currentActionCallback = null;
let expectedCode = '';
let chartGlobal = null;
let chartWishes = null;
let chartDist = null;

export function requireConfirmation(description, callback) {
    const modal = document.getElementById('confirmActionModal');
    const descEl = document.getElementById('confirmActionDescription');
    const codeDisplay = document.getElementById('confirmActionCodeDisplay');
    const codeInput = document.getElementById('confirmActionCodeInput');
    const btnConfirm = document.getElementById('confirmActionButton');

    expectedCode = Math.random().toString(36).substring(2, 8).toUpperCase();

    descEl.textContent = description;
    codeDisplay.textContent = expectedCode;
    codeInput.value = '';
    btnConfirm.disabled = true;
    btnConfirm.classList.add('opacity-50', 'cursor-not-allowed');

    currentActionCallback = callback;
    modal.classList.remove('hidden');

    setTimeout(() => codeInput.focus(), 100);
}

export function initConfirmationListeners() {
    document.getElementById('confirmActionCodeInput').addEventListener('input', (e) => {
        const val = e.target.value.trim().toUpperCase();
        const btnConfirm = document.getElementById('confirmActionButton');
        if (val === expectedCode) {
            btnConfirm.disabled = false;
            btnConfirm.classList.remove('opacity-50', 'cursor-not-allowed');
        } else {
            btnConfirm.disabled = true;
            btnConfirm.classList.add('opacity-50', 'cursor-not-allowed');
        }
    });

    document.getElementById('confirmActionButton').addEventListener('click', () => {
        if (!document.getElementById('confirmActionButton').disabled && currentActionCallback) {
            document.getElementById('confirmActionModal').classList.add('hidden');
            currentActionCallback();
        }
    });
}

export function openProcedureModal() {
    document.getElementById('procedureModal').classList.remove('hidden');
    window.fetchSubmittedStudents();
    window.fetchAssignedStudents();
    window.fetchGlobalFilieres().then(() => window.fetchMobilityQuotas());
}

export function toggleDiagnostics() {
    const modal = document.getElementById('diagnosticsModal');
    if (modal.classList.contains('hidden')) {
        modal.classList.remove('hidden');
        loadDiagnostics();
    } else {
        modal.classList.add('hidden');
    }
}

export async function loadDiagnostics() {
    try {
        const response = await fetch('/api.php?path=/university/admin/mobility/diagnostics');
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        const data = await response.json();

        if (chartGlobal) chartGlobal.destroy();
        if (chartWishes) chartWishes.destroy();
        if (chartDist) chartDist.destroy();

        const ctxGlobal = document.getElementById('chartGlobalStatus').getContext('2d');
        chartGlobal = new Chart(ctxGlobal, {
            type: 'pie',
            data: {
                labels: ['Mobilités déjà validées', 'Mobilités non validées'],
                datasets: [{
                    data: [data.validated_mobility, data.remaining_students],
                    backgroundColor: ['#3b82f6', '#9ca3af'],
                    borderWidth: (data.validated_mobility > 0 && data.remaining_students > 0) ? 1 : 0,
                }],
            },
            plugins: [ChartDataLabels],
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 10 } } },
                    datalabels: {
                        color: '#ffffff',
                        font: { weight: 'bold', size: 14 },
                        formatter(value) {
                            return value > 0 ? value : null;
                        },
                    },
                },
            },
        });

        const ctxWishes = document.getElementById('chartWishesStatus').getContext('2d');
        const activeWishesSlices = [data.wishes_submitted, data.wishes_in_progress, data.retardataires].filter((v) => v > 0).length;
        chartWishes = new Chart(ctxWishes, {
            type: 'pie',
            data: {
                labels: ['Vœux soumis', 'En cours (non soumis)', 'Retardataires (0 vœu)'],
                datasets: [{
                    data: [data.wishes_submitted, data.wishes_in_progress, data.retardataires],
                    backgroundColor: ['#22c55e', '#f59e0b', '#ef4444'],
                    borderWidth: activeWishesSlices > 1 ? 1 : 0,
                }],
            },
            plugins: [ChartDataLabels],
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 10 } } },
                    datalabels: {
                        color: '#ffffff',
                        font: { weight: 'bold', size: 14 },
                        formatter(value) {
                            return value > 0 ? value : null;
                        },
                    },
                },
            },
        });

        const ctxDist = document.getElementById('chartWishesDistribution').getContext('2d');
        const dist = data.wishes_distribution;
        chartDist = new Chart(ctxDist, {
            type: 'bar',
            data: {
                labels: ['1 vœu', '2 vœux', '3 vœux', '4 vœux', '5 vœux'],
                datasets: [{
                    label: "Nombre d'étudiants",
                    data: [dist['1'], dist['2'], dist['3'], dist['4'], dist['5']],
                    backgroundColor: '#6366f1',
                    borderRadius: 4,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1 } },
                },
                plugins: {
                    legend: { display: false },
                },
            },
        });
    } catch (error) {
        console.error('Erreur lors du chargement des diagnostiques:', error);
    }
}
