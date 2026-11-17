import {
    fetchAssignment,
    fetchCampaignStatus,
    fetchStudentQuota,
    fetchUniversities,
} from './api.js';
import { flyToUniversity, updateMap } from './map.js';
import {
    addUniversityToWishes,
    deleteWish,
    moveWish,
    refreshWishesFromServer,
    renderWishesList,
    submitDecision,
    submitWishes,
    wishedUniversities,
} from './wishes.js';

const popupState = new Map();
window.MobilityMapState = {
    popupState,
    wishedUniversities,
};

const campaignOpen = await fetchCampaignStatus();
window.MobilityMapState.campaignOpen = campaignOpen;

if (campaignOpen) {
    const badge = document.getElementById('campaignOpenBadge');
    if (badge) badge.classList.remove('hidden');
} else {
    const banner = document.getElementById('campaignClosedBanner');
    const notice = document.getElementById('campaignClosedNotice');
    const wishesEmpty = document.getElementById('wishesEmpty');
    const wishesList = document.getElementById('wishesList');
    const wishesCount = document.getElementById('wishesCount');
    const wishesBtn = document.getElementById('wishesBtn');
    const wishesPanel = document.getElementById('wishesPanel');

    if (banner) banner.classList.remove('hidden');
    if (notice) notice.classList.remove('hidden');
    if (wishesEmpty) wishesEmpty.classList.add('hidden');
    if (wishesList) wishesList.classList.add('hidden');
    if (wishesCount) wishesCount.classList.add('hidden');
    if (wishesBtn) wishesBtn.classList.add('hidden');
    if (wishesPanel) wishesPanel.classList.add('hidden');
}

const universities = await fetchUniversities();
const universitiesById = new Map(
    universities.map((u) => [String(u.id_partner_university), u])
);
window.MobilityMapState.universities = universities;
window.MobilityMapState.universitiesById = universitiesById;

const assignment = await fetchAssignment();
window.MobilityMapState.assignment = assignment;

await refreshWishesFromServer();

window.addUniversityToWishes = addUniversityToWishes;
window.deleteWish = deleteWish;
window.moveWish = moveWish;
window.submitWishes = submitWishes;
window.submitDecision = submitDecision;
window.flyToUniversity = flyToUniversity;
window.updateMap = () => updateMap(universities);

renderWishesList();
if (campaignOpen && !assignment) {
    fetchStudentQuota();
}
updateMap(universities);

if (assignment) {
    const mapControls = document.getElementById('mapControls');
    if (mapControls) mapControls.classList.add('hidden');
    document.getElementById('filterForm').classList.add('hidden');
    document.getElementById('wishesPanel').classList.add('hidden');

    setTimeout(() => {
        window.flyToUniversity(assignment.id_partner_university);
    }, 500);
}
