    <!-- ===================== MODALS ===================== -->
    <?php foreach ($etudiants as $e):
        $isEdit = (bool)$e['entreprise'] && $user['type'] === 'administratif';
        $modalTitle = $isEdit ? 'Modifier le stage' : 'Détail du stage';
    ?>
    <div id="modal-<?= $e['id_etudiant'] ?>" tabindex="-1" aria-hidden="true"
        class="hidden overflow-y-auto overflow-x-hidden fixed top-0 right-0 left-0 z-50 justify-center items-center w-full md:inset-0 h-[calc(100%-1rem)] max-h-full">
        <div class="relative p-4 w-full max-w-5xl max-h-full">
            <div class="relative bg-white rounded-2xl shadow">

                <!-- Header -->
                <div class="flex items-center justify-between p-6 border-b border-gray-200 bg-primary text-on-primary rounded-tl-2xl rounded-tr-2xl">
                    <div>
                        <h3 class="text-lg font-bold"><?= $modalTitle ?></h3>
                        <p class="text-sm mt-0.5"><?= $t->e($e['student_fullname']) ?> · <?= $t->e($e['filiere']) ?></p>
                    </div>
                    <button data-modal-hide="modal-<?= $e['id_etudiant'] ?>"
                        class="bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 inline-flex justify-center items-center">
                        <svg class="w-3 h-3" fill="none" viewBox="0 0 14 14"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"/></svg>
                    </button>
                </div>

                <!-- Formulaire -->
                <form action="<?= $t->router->href("dashboard-stage-post") ?>" method="POST" class="p-6 space-y-5">
                    <input type="hidden" name="id_stage" value="<?= $t->e($e['id_stage'] ?? '') ?>">
                    <input type="hidden" name="id_etudiant" value="<?= $e['id_etudiant'] ?>">

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div class="col-span-full">
                            <label class="block mb-2 text-sm font-medium text-gray-900">Entreprise <span class="text-red-500">*</span></label>
                            <input type="text" name="entreprise"
                                value="<?= $t->e($e['entreprise'] ?? '') ?>"
                                placeholder="Nom de l'entreprise"
                                required
                                <?= $isEdit ? '' : 'disabled' ?>
                                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"/>
                        </div>
                        <div>
                            <label class="block mb-2 text-sm font-medium text-gray-900">Intitulé <span class="text-red-500">*</span></label>
                            <input type="text" name="intitulé"
                                value="<?= $t->e($e['intitulé'] ?? '') ?>"
                                placeholder="Intitulé du poste"
                                required
                                <?= $isEdit ? '' : 'disabled' ?>
                                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"/>
                        </div>
                        <div>
                            <label class="block mb-2 text-sm font-medium text-gray-900">Nature <span class="text-red-500">*</span></label>
                            <input type="text" name="nature"
                                value="<?= $t->e($e['nature'] ?? '') ?>"
                                placeholder="Nature du poste"
                                required
                                <?= $isEdit ? '' : 'disabled' ?>
                                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"/>
                        </div>
                        <div>
                            <label class="block mb-2 text-sm font-medium text-gray-900">Date de début <span class="text-red-500">*</span></label>
                            <input type="date" name="date_debut"
                                value="<?= $t->e($e['date_debut'] ?? $e['date_debut']) ?>"
                                required
                                <?= $isEdit ? '' : 'disabled' ?>
                                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"/>
                        </div>
                        <div>
                            <label class="block mb-2 text-sm font-medium text-gray-900">Date de fin <span class="text-red-500">*</span></label>
                            <input type="date" name="date_fin"
                                value="<?= $t->e($e['date_fin'] ?? '') ?>"
                                required
                                <?= $isEdit ? '' : 'disabled' ?>
                                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"/>
                        </div>
                        <div class="col-span-full">
                            <label class="block mb-2 text-sm font-medium text-gray-900">Description <span class="text-red-500">*</span></label>
                            <textarea name="description" id="" required <?= $isEdit ? '' : 'disabled' ?>
                                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"><?= $t->e($e['description'] ?? '') ?></textarea>
                        </div>
                    </div>

                    <div class="pt-2 border-t border-gray-100">
                        <p class="text-sm font-semibold text-gray-700 mb-4">
                            Adresse du stage
                            <?php if (!$isEdit): ?>
                                <span class="font-normal text-gray-500">(optionnel)</span>
                            <?php endif; ?>
                        </p>
                        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                            <div class="col-span-full">
                                <label class="block mb-2 text-sm font-medium text-gray-900">Adresse</label>
                                <input type="text" name="adresse"
                                    value="<?= $t->e($e['adresse'] ?? '') ?>"
                                    placeholder="Adresse du stage"
                                    <?= $isEdit ? '' : 'disabled' ?>
                                    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"/>
                            </div>
                            <div>
                                <label class="block mb-2 text-sm font-medium text-gray-900">Code postal</label>
                                <input type="text" name="code_postal"
                                    value="<?= $t->e($e['code_postal'] ?? '') ?>"
                                    placeholder="Code postal"
                                    <?= $isEdit ? '' : 'disabled' ?>
                                    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"/>
                            </div>
                            <div>
                                <label class="block mb-2 text-sm font-medium text-gray-900">Ville <span class="text-red-500">*</span></label>
                                <input type="text" name="ville"
                                    value="<?= $t->e($e['ville'] ?? '') ?>"
                                    placeholder="Ville du stage"
                                    required
                                    <?= $isEdit ? '' : 'disabled' ?>
                                    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"/>
                            </div>
                            <div>
                                <label class="block mb-2 text-sm font-medium text-gray-900">Pays</label>
                                <input type="text" name="pays"
                                    value="<?= $t->e($e['pays'] ?? '') ?>"
                                    placeholder="Pays du stage"
                                    <?= $isEdit ? '' : 'disabled' ?>
                                    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"/>
                            </div>
                        </div>
                    </div>

                    <!-- Tuteur -->
                    <div class="pt-2 border-t border-gray-100">
                        <p class="text-sm font-semibold text-gray-700 mb-4">
                            Tuteur entreprise
                            <?php if (!$isEdit): ?>
                                <span class="font-normal text-gray-500">(optionnel)</span>
                            <?php endif; ?>
                        </p>
                        <div class="grid grid-cols-1 gap-4">
                            <div>
                                <label class="block text-xs font-medium text-slate-600 mb-1.5" for="id_enseignant">Nom du tuteur</label>
                                <select id="id_enseignant" name="id_enseignant"
                                        <?= $isEdit ? '' : 'disabled' ?>
                                        class="w-full text-sm text-[#0f2744] bg-slate-50 border border-black/10 rounded-lg px-3 py-2.5 outline-none focus:border-blue-500 focus:bg-white transition-colors">
                                    <option value="">Aucun</option>
                                    <?php foreach ($enseignants as $ens): ?>
                                        <option value="<?= $ens['id_enseignant'] ?>"
                                            <?= ($e['id_enseignant'] ?? '') == $ens['id_enseignant'] ? 'selected' : '' ?>>
                                            <?= htmlspecialchars($ens['nom'] . ' ' . $ens['prenom']) ?>
                                        </option>
                                    <?php endforeach; ?>
                                </select>
                            </div>
                        </div>
                    </div>

                    <!-- Footer -->
                    <?php if ($user['type'] === 'administratif'): ?>
                        <div class="flex items-center justify-end gap-3 pt-4 border-t border-gray-100">
                            <button type="button" data-modal-hide="modal-<?= $e['id_etudiant'] ?>"
                                class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition">
                                Annuler
                            </button>
                            <button type="submit"
                                class="px-4 py-2 text-sm font-medium text-white rounded-lg focus:ring-4 transition bg-blue-600 hover:bg-blue-700 focus:ring-blue-300">
                                Enregistrer
                            </button>
                        </div>
                    <?php endif; ?>

                </form>
            </div>
        </div>
    </div>
    <?php endforeach; ?>
