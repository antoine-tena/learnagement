<?php $t->extend('layouts/dashboard'); ?>

<?php $t->startSlot('title'); ?>Gestion des stages<?php $t->endSlot(); ?>

<?php $t->startSlot('content'); ?>

<?php
    $token = $user["jwt_token"];

    $enseignants = get_enseignants($token);

//$etudiants = get_stages($token);
$etudiants = get_stages2($token);

$total       = count($etudiants);
$sans_stage  = array_values(array_filter($etudiants, fn($e) => $e['status'] === 'no-internship'));
$sans_tuteur = array_values(array_filter($etudiants, fn($e) => $e['status'] === 'pending'));
$complets    = array_values(array_filter($etudiants, fn($e) => $e['status'] === 'completed'));

$filtre    = $_GET['filtre'] ?? 'tous';
$recherche = $_GET['q'] ?? '';
$filtre_enseignant = $_GET['id_enseignant'] ?? '';

$liste = match($filtre) {
    'sans_stage'  => $sans_stage,
    'sans_tuteur' => $sans_tuteur,
    'complet'     => $complets,
    default       => $etudiants,
};

if ($recherche !== '' || $filtre_enseignant !== '') {
    $liste = array_values(array_filter($liste, function($e) use ($recherche, $filtre_enseignant) {
        // Filtre enseignant — doit correspondre exactement si renseigné
        if ($filtre_enseignant !== '' && (string)($e['id_enseignant'] ?? '') !== $filtre_enseignant)
            return false;

        // Filtre recherche — au moins un champ doit correspondre si renseigné
        if ($recherche !== '') {
            $q = strtolower($recherche);
            $match =
                str_contains(strtolower($e['student_fullname'] ?? ''), $q) ||
                str_contains(strtolower($e['mail']             ?? ''), $q) ||
                str_contains(strtolower($e['filiere']          ?? ''), $q) ||
                str_contains(strtolower($e['entreprise']       ?? ''), $q);
            if (!$match)
                return false;
        }
        return true;
    }));
}
?>
<section class="flex flex-col grow relative m-8">
    <div>
        <?php include __DIR__ . '/stage/kpis_toolbar.php'; ?>
        <?php include __DIR__ . '/stage/table.php'; ?>
    </div>

    <?php include __DIR__ . '/stage/modals.php'; ?>
</section>
<?php $t->endSlot(); ?>
