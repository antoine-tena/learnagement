<?php $t->extend('layouts/dashboard'); ?>

<?php $t->startSlot('title'); ?>Carte de Mobilité — Learnagement<?php $t->endSlot(); ?>

<?php $t->startSlot('content'); ?>
<section class="relative flex-1 min-h-[70vh]">
    <!-- Map component -->
    <div id="map" class="absolute inset-0" style="height: 100%; width: 100%;"></div>

    <!-- Street View Modal (grand format) -->
    <div id="streetViewModal" class="streetview-modal">
        <div class="streetview-content">
            <div class="streetview-header">
                <h2 id="streetViewTitle" class="text-lg font-semibold"></h2>
                <button class="streetview-close" onclick="window.closeStreetViewModal()">x</button>
            </div>
            <div id="streetViewPanoramaModal" style="width: 100%; height: 100%;"></div>
        </div>
    </div>

    <!-- Quota Display (Bottom Left) -->
    <div id="studentQuotaContainer" class="hidden absolute bottom-6 left-4 z-[1000] bg-white/95 border border-indigo-100 rounded-lg shadow-lg p-4 backdrop-blur-sm pointer-events-none">
        <p class="text-[10px] uppercase font-bold text-indigo-700 tracking-wide mb-1">Quota - <span id="quotaFiliereName">...</span></p>
        <div class="flex gap-4">
            <div class="flex items-center gap-1">
                <span class="text-xs font-semibold text-indigo-600">S8:</span>
                <span class="text-sm font-bold text-indigo-900" id="quotaS8Count">-</span>
            </div>
            <div class="flex items-center gap-1">
                <span class="text-xs font-semibold text-indigo-600">S9:</span>
                <span class="text-sm font-bold text-indigo-900" id="quotaS9Count">-</span>
            </div>
        </div>
    </div>

    <!-- Contrôles et panneaux superposés -->
    <div class="absolute top-[10px] left-[55px] z-[1000] flex max-w-[92vw] flex-col items-start gap-2.5">
        <div id="mapControls" class="flex items-center gap-2">
            <button onclick="document.getElementById('filterForm').classList.toggle('hidden')"
                class="bg-white hover:bg-gray-100 text-gray-800 font-semibold py-2 px-4 border border-gray-400 rounded shadow text-sm">
                Filtres
            </button>
            <button id="wishesBtn" onclick="document.getElementById('wishesPanel').classList.toggle('hidden')"
                class="bg-white hover:bg-gray-100 text-gray-800 font-semibold py-2 px-4 border border-gray-400 rounded shadow text-sm">
                Voeux
            </button>
            <div id="campaignOpenBadge" class="hidden bg-blue-50 text-blue-800 font-semibold py-2 px-4 border border-blue-200 rounded shadow text-sm flex items-center gap-2 pointer-events-none">
                <span class="text-blue-500">ℹ️</span> Campagne en cours
            </div>
            <div id="wishesSubmittedBadge" class="hidden bg-green-50 text-green-800 font-semibold py-2 px-4 border border-green-200 rounded shadow text-sm flex items-center gap-2 pointer-events-none">
                <span class="text-green-500">✅</span> Vœux soumis
            </div>
        </div>

        <form id="filterForm" onsubmit="return false;" class="hidden bg-white p-4 rounded-lg shadow-lg border border-gray-200">
            <div class="flex flex-wrap justify-center items-center gap-4">
                <div class="flex flex-col">
                    <label for="semestreSelect" class="text-xs font-semibold text-gray-600 mb-1">Semestre</label>
                    <select name="semestre" id="semestreSelect" onchange="updateMap()" class="border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-primary min-w-24">
                    <option>Tous</option>
                    <option value="S8">S8</option>
                    <option value="S9">S9</option>
                    </select>
                </div>
                <div class="flex flex-col">
                    <div class="flex justify-between items-center mb-1">
                        <label for="noteMinRange" class="text-xs font-semibold text-gray-600">Note minimale</label>
                        <span id="noteMinValue" class="text-xs font-bold text-gray-700">20</span>
                    </div>
                    <input type="range" name="notemin" id="noteMinRange" min="0" max="20" value="20" class="w-32 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary" oninput="document.getElementById('noteMinValue').innerText = this.value; updateMap()">
                </div>
            </div>
        </form>

        <aside id="wishesPanel" class="hidden w-[min(92vw,22rem)] max-h-[80vh] overflow-y-auto bg-white/95 p-4 rounded-lg shadow-lg border border-gray-200 backdrop-blur-sm">
            <div class="mb-3 flex items-center justify-between">
                <h2 class="text-sm font-semibold text-gray-800">Mes voeux</h2>
                <span id="wishesCount" class="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-semibold text-primary">0/5</span>
            </div>
            <div id="campaignClosedNotice" class="hidden mb-3 bg-amber-50 border border-amber-200 rounded-lg p-3">
                <p class="text-xs font-bold text-amber-800">Inscriptions non disponibles.</p>
                <p class="text-xs text-amber-700 mt-0.5">La campagne n'est pas encore lancée. Revenez après l'annonce
                    officielle pour soumettre vos vœux.</p>
            </div>
            <p id="wishesEmpty" class="text-sm text-gray-500">Aucun voeu pour le moment.</p>
            <ul id="wishesList" class="space-y-2"></ul>
        </aside>
    </div>
    <!-- Bannière campagne non ouverte -->
    <div id="campaignClosedBanner" class="hidden absolute top-3 left-1/2 -translate-x-1/2 z-[1100] w-max max-w-[90vw] pointer-events-none">
        <div class="bg-white border border-amber-300 rounded-xl shadow-lg px-5 py-3 flex items-center gap-3">
            <span class="text-amber-500 text-xl">⏳</span>
            <div>
                <p class="text-sm font-bold text-gray-800">La procédure de mobilité n'a pas encore commencé.</p>
                <p class="text-xs text-gray-500 mt-0.5">Vous pouvez explorer les universités. L'inscription aux vœux sera disponible après le lancement officiel de la campagne.</p>
            </div>
        </div>
    </div>
</section>
<?php $t->endSlot(); ?>


<?php $t->startSlot('stylesheet'); ?>
<!-- Import Leaflet CSS -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
crossorigin=""/>
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
<link rel="stylesheet" href="/theme/mobility-map.css" />
<?php $t->endSlot(); ?>


<?php $t->startSlot('script.top'); ?>
<?php
    $googleMapsApiKey = getenv('GOOGLE_MAPS_API_KEY') ?: ($_ENV['GOOGLE_MAPS_API_KEY'] ?? '');
?>
<!-- Import Leaflet JS -->
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
    integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
    crossorigin="">
</script>
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>

<!-- Google Maps API pour Street View interactif -->
<script src="https://maps.googleapis.com/maps/api/js?key=<?= urlencode($googleMapsApiKey) ?>&libraries=places"></script>

<!-- Logic map dédiée -->
<script src="/theme/mobility-map-carousel.js"></script>
<script src="/theme/mobility-map-streetview/places.js"></script>
<script src="/theme/mobility-map-streetview/ui.js"></script>

<!-- ToDo : Déplacer dans un fichier global ex db.js -->
<script>
    window.ENV = {
        //BACKEND_URL: "<?= getenv('INSTANCE_PROTOCOL') . '://' . getenv('INSTANCE_URL') ?>",
        //BACKEND_PORT: "<?= getenv('BACKEND_PYTHON_PORT') ?>",
        //USER_TOKEN: "<?= $_SESSION["jwt_token"] ?>",
        USER_ID: "<?= $_SESSION["id"] ?>"
    };
    console.log("Environnement chargé :", window.ENV);
</script>
<?php $t->endSlot(); ?>

<?php $t->startSlot('script.bottom'); ?>
<script type="module" defer src="/scripts/mobility-map/main.js"></script>
<?php $t->endSlot(); ?>
