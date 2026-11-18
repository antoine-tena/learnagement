<?php $t->extend('layouts/dashboard'); ?>

<?php $t->startSlot('title'); ?>Rendu — Learnagement<?php $t->endSlot(); ?>

<?php $t->startSlot('content'); ?>
<?php
    $token = $user["jwt_token"];
    $id = $user['id'];

    $rendus = get_rendus_enseignant($token, $id);
?>

<div class="p-4 space-y-8">
    <!-- Titre principal -->
    <h1 class="text-3xl font-bold text-gray-800 border-b pb-3">
        Enseignants
    </h1>

    <!-- Sous-titre -->
    <h2 class="text-2xl font-semibold text-blue-700">
        Liste des rendus vous concernant
    </h2>

    <?php if (empty($rendus)): ?>
        <p class='bg-green-50 border border-green-300 text-green-800 rounded-lg p-4'>
            🎉 Aucun rendu à venir pour le moment.
        </p>
    <?php else: ?>
        <?php foreach ($rendus as $rendu): ?>
            <div class='flex flex-col md:flex-row md:items-center md:justify-between
                    border rounded-lg p-4 hover:bg-gray-50 transition'>

                <div class='space-y-1'>
                    <p class='font-semibold text-gray-800'>
                        <?= htmlspecialchars($rendu['description']) ?>
                    </p>
                    <p class='text-sm text-gray-500'>
                        Promotion : <?= htmlspecialchars($rendu['promo']) ?>
                    </p>
                </div>

                <div class='mt-2 md:mt-0'>
                    <span class='inline-block bg-indigo-100 text-indigo-800
                                    px-3 py-1 rounded-full text-sm font-medium'>
                        À rendre le <?= htmlspecialchars($rendu['date']) ?>
                    </span>
                </div>
            </div>
        <?php endforeach; ?>
    <?php endif; ?>
</div>

<?php $t->endSlot(); ?>
