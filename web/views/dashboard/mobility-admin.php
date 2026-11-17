<?php $t->extend('layouts/dashboard'); ?>

<?php $t->startSlot('title'); ?>Gestion des Mobilités — Learnagement<?php $t->endSlot(); ?>

<?php $t->startSlot('content'); ?>
<section class="flex flex-col grow relative m-8 gap-6">
    <?php include __DIR__ . '/mobility-admin/header_kpis.php'; ?>
    <?php include __DIR__ . '/mobility-admin/map_section.php'; ?>
    <?php include __DIR__ . '/mobility-admin/universities_panel.php'; ?>
    <?php include __DIR__ . '/mobility-admin/procedure_modal.php'; ?>
    <?php include __DIR__ . '/mobility-admin/wishes_modal.php'; ?>
    <?php include __DIR__ . '/mobility-admin/campaign_modals.php'; ?>
</section>
<?php $t->endSlot(); ?>


<?php $t->startSlot('stylesheet'); ?>
<!-- Import Leaflet CSS -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
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
    integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin="">
    </script>
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>

<!-- Google Maps API pour Street View interactif -->
<script src="https://maps.googleapis.com/maps/api/js?key=<?= urlencode($googleMapsApiKey) ?>&libraries=places"></script>

<!-- Logic map dédiée -->
<script src="/theme/mobility-map-carousel.js"></script>
<script src="/theme/mobility-map-streetview.js"></script>

<!-- ToDo : Déplacer dans un fichier global ex db.js -->

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>

<script>
    window.ENV = {
        //BACKEND_URL: "<?= getenv('INSTANCE_PROTOCOL') . '://' . getenv('BACKEND_PYTHON_DOCKER_URL') ?>",
        //BACKEND_PORT: "<?= getenv('BACKEND_PYTHON_DOCKER_PORT') ?>",
        //USER_TOKEN: "<?= $_SESSION["jwt_token"] ?>",
        USER_ID: "<?= $_SESSION["id"] ?>"
    };
    console.log("Environnement chargé :", window.ENV);
</script>
<?php $t->endSlot(); ?>

<?php $t->startSlot('script.bottom'); ?>
<script type="module" defer src="/scripts/mobility-admin/main.js"></script>
<?php $t->endSlot(); ?>
