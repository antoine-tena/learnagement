import { refreshAllData } from './api.js';
import {
    closeAssignmentPhase,
    fetchAssignedStudents,
    renderEtape3Chart,
    runAssignmentExec,
    runAssignmentUI,
    updateAssignmentStatusExec,
} from './assignment.js';
import {
    addDoublantToList,
    fetchSubmittedStudents,
    forceSubmitWishesExec,
    forceSubmitWishesUI,
    launchCampaign,
    launchCampaignExec,
    removeDoublant,
    renderDoublantsList,
    resetStudentWishes,
} from './campaign.js';
import {
    initConfirmationListeners,
    loadDiagnostics,
    openProcedureModal,
    requireConfirmation,
    toggleDiagnostics,
} from './diagnostics.js';
import {
    exportAssignedData,
    exportAssignments,
    exportDiagnosticData,
    exportPlaces,
    exportUnassignedData,
    exportWishes,
} from './exports.js';
import { flyToUniversity, scrollToUniversityOnMap, updateMap } from './map.js';
import {
    fetchGlobalFilieres,
    fetchMobilityQuotas,
    loadQuotas,
    renderMobilityQuotas,
    saveMobilityQuotas,
    saveQuotas,
} from './quotas.js';
import {
    addNewUniversityPlaceRow,
    resetAddUniversityForm,
    saveNewUniversity,
} from './universities_create.js';
import {
    addUniversityPlace,
    removeUniversityPlace,
    renderUniversitiesAdminTable,
    saveUniversityDraft,
    toggleUniversityPlacesEditor,
    updateUniversityMeta,
    updateUniversityPlace,
} from './universities_table.js';
import {
    renderDashboardTable,
    toggleWishDetails,
    toggleWishesModal,
} from './wishes_table.js';

window.toggleWishDetails = toggleWishDetails;
window.toggleWishesModal = toggleWishesModal;
window.toggleUniversityPlacesEditor = toggleUniversityPlacesEditor;
window.updateUniversityMeta = updateUniversityMeta;
window.updateUniversityPlace = updateUniversityPlace;
window.removeUniversityPlace = removeUniversityPlace;
window.addUniversityPlace = addUniversityPlace;
window.saveUniversityDraft = saveUniversityDraft;
window.addNewUniversityPlaceRow = addNewUniversityPlaceRow;
window.saveNewUniversity = saveNewUniversity;
window.flyToUniversity = flyToUniversity;
window.scrollToUniversityOnMap = scrollToUniversityOnMap;
window.updateMap = updateMap;
window.forceSubmitWishesExec = forceSubmitWishesExec;
window.forceSubmitWishesUI = forceSubmitWishesUI;
window.fetchMobilityQuotas = fetchMobilityQuotas;
window.saveMobilityQuotas = saveMobilityQuotas;
window.fetchGlobalFilieres = fetchGlobalFilieres;
window.renderMobilityQuotas = renderMobilityQuotas;
window.saveQuotas = saveQuotas;
window.loadQuotas = loadQuotas;
window.runAssignmentExec = runAssignmentExec;
window.runAssignmentUI = runAssignmentUI;
window.exportWishes = exportWishes;
window.exportAssignments = exportAssignments;
window.exportPlaces = exportPlaces;
window.exportAssignedData = exportAssignedData;
window.exportUnassignedData = exportUnassignedData;
window.exportDiagnosticData = exportDiagnosticData;
window.openProcedureModal = openProcedureModal;
window.fetchSubmittedStudents = fetchSubmittedStudents;
window.addDoublantToList = addDoublantToList;
window.removeDoublant = removeDoublant;
window.renderDoublantsList = renderDoublantsList;
window.launchCampaignExec = launchCampaignExec;
window.launchCampaign = launchCampaign;
window.resetStudentWishes = resetStudentWishes;
window.fetchAssignedStudents = fetchAssignedStudents;
window.updateAssignmentStatusExec = updateAssignmentStatusExec;
window.renderEtape3Chart = renderEtape3Chart;
window.requireConfirmation = requireConfirmation;
window.toggleDiagnostics = toggleDiagnostics;
window.loadDiagnostics = loadDiagnostics;
window.closeAssignmentPhase = closeAssignmentPhase;

document.getElementById('wishesSearch').addEventListener('input', renderDashboardTable);
document.getElementById('dossierStatusFilter').addEventListener('change', renderDashboardTable);
const assignmentStatusFilterElem = document.getElementById('assignmentStatusFilter');
if (assignmentStatusFilterElem) assignmentStatusFilterElem.addEventListener('change', renderDashboardTable);
const wishesFiliereFilter = document.getElementById('wishesFiliereFilter');
if (wishesFiliereFilter) wishesFiliereFilter.addEventListener('change', renderDashboardTable);
document.getElementById('filiereSelect').addEventListener('change', updateMap);
document.getElementById('universityAdminSearch').addEventListener('input', renderUniversitiesAdminTable);
document.getElementById('addUniversityRowBtn').addEventListener('click', () => {
    const panel = document.getElementById('addUniversityPanel');
    panel.classList.toggle('hidden');
});
document.getElementById('cancelAddUniversityBtn').addEventListener('click', () => {
    document.getElementById('addUniversityPanel').classList.add('hidden');
});

document.getElementById('saveNewUniversityBtn').addEventListener('click', saveNewUniversity);
document.getElementById('resetDashboardFilters').addEventListener('click', () => {
    document.getElementById('wishesSearch').value = '';
    document.getElementById('dossierStatusFilter').value = 'tous';
    if (document.getElementById('assignmentStatusFilter')) document.getElementById('assignmentStatusFilter').value = 'tous';
    if (document.getElementById('wishesFiliereFilter')) document.getElementById('wishesFiliereFilter').value = 'toutes';
    document.getElementById('filiereSelect').value = 'toutes';
    document.getElementById('semestreSelect').value = 'Tous';
    document.getElementById('noteMinRange').value = 20;
    document.getElementById('noteMinValue').innerText = 20;
    renderDashboardTable();
    updateMap();
});

initConfirmationListeners();
await refreshAllData();
resetAddUniversityForm();
