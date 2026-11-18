async function downloadExport(path, filenamePrefix) {
    try {
        const response = await fetch(`/api.php?path=${path}`);
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `${filenamePrefix}_${new Date().toISOString().slice(0, 10)}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        alert('Erreur de connexion.');
    }
}

export async function exportWishes() {
    await downloadExport('/university/admin/wishes/export', 'Export_Voeux_Mobilite');
}

export async function exportAssignments() {
    await downloadExport('/university/admin/assignments/export', 'Export_Affectations_Mobilite');
}

export async function exportPlaces() {
    await downloadExport('/university/admin/places/export', 'Export_Etat_Places');
}

export async function exportAssignedData(status) {
    await downloadExport(
        `/university/admin/mobility/assigned-students/export/${status}`,
        `Export_Affectations_${status}`
    );
}

export async function exportUnassignedData() {
    await downloadExport(
        '/university/admin/mobility/unassigned-students/export',
        'Export_Non_Affectes'
    );
}

export async function exportDiagnosticData(category) {
    await downloadExport(
        `/university/admin/mobility/diagnostics/export/${category}`,
        `Export_Mobilite_Stats_${category}`
    );
}
