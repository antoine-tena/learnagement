        <!-- En-tête -->
        <div class="mb-8">
            <h1 class="text-3xl font-extrabold">Gestion des stages</h1>
            <p class="mt-1">Suivi et administration des stages étudiants · Promotion 2023–2024</p>
        </div>

        <!-- KPIs cliquables -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">

            <a href="?filtre=tous" class="block rounded-2xl p-5 border <?= $filtre === 'tous' ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200' ?> hover:shadow-md transition">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-sm font-medium text-gray-600">Total étudiants</span>
                    <span class="bg-blue-100 p-2 rounded-lg">
                        <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                    </span>
                </div>
                <div class="text-4xl font-extrabold text-gray-900"><?= $total ?></div>
                <div class="mt-1 text-xs">Tous les étudiants</div>
            </a>

            <a href="?filtre=sans_stage" class="block rounded-2xl p-5 border <?= $filtre === 'sans_stage' ? 'border-red-500 ring-2 ring-red-200' : 'border-gray-200' ?> hover:shadow-md transition">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-sm font-medium text-gray-600">Sans stage</span>
                    <span class="bg-red-100 p-2 rounded-lg">
                        <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                    </span>
                </div>
                <div class="text-4xl font-extrabold text-red-600"><?= count($sans_stage) ?></div>
                <div class="mt-1 text-xs"><?= $total > 0 ? round(count($sans_stage) / $total * 100) : 0 ?>% du total</div>
            </a>

            <a href="?filtre=sans_tuteur" class="block rounded-2xl p-5 border <?= $filtre === 'sans_tuteur' ? 'border-yellow-500 ring-2 ring-yellow-200' : 'border-gray-200' ?> hover:shadow-md transition">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-sm font-medium text-gray-600">Sans tuteur</span>
                    <span class="bg-yellow-100 p-2 rounded-lg">
                        <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                    </span>
                </div>
                <div class="text-4xl font-extrabold text-yellow-600"><?= count($sans_tuteur) ?></div>
                <div class="mt-1 text-xs"><?= $total > 0 ? round(count($sans_tuteur) / $total * 100) : 0 ?>% du total</div>
            </a>

            <a href="?filtre=complet" class="block rounded-2xl p-5 border <?= $filtre === 'complet' ? 'border-green-500 ring-2 ring-green-200' : 'border-gray-200' ?> hover:shadow-md transition">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-sm font-medium text-gray-600">Stage complet</span>
                    <span class="bg-green-100 p-2 rounded-lg">
                        <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                    </span>
                </div>
                <div class="text-4xl font-extrabold text-green-600"><?= count($complets) ?></div>
                <div class="mt-1 text-xs"><?= $total > 0 ? round(count($complets) / $total * 100) : 0 ?>% du total</div>
            </a>

        </div>

        <!-- Barre d'outils -->
        <div class="bg-white border border-black/8 rounded-xl mb-5">
            <form method="GET">
                <input type="hidden" name="filtre" value="<?= $t->e($filtre) ?>">
                <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 p-3">

                    <!-- Recherche -->
                    <div class="relative flex-1 border border-black/8 rounded-lg py-2">
                        <?= $t->component("search_bar", props: [
                            "size" => "lg",
                            "value"=> $t->e($recherche),
                            "placeholder" => "Rechercher un étudiant, entreprise..."
                        ]) ?>
                    </div>

                    <!-- Filtre enseignant -->
                    <div class="relative">
                        <div class="absolute inset-y-0 left-3 flex items-center pointer-events-none">
                            <svg width="14" height="14" fill="none" viewBox="0 0 24 24">
                                <circle cx="12" cy="8" r="4" stroke="#94a3b8" stroke-width="1.8"/>
                                <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke="#94a3b8" stroke-width="1.8" stroke-linecap="round"/>
                            </svg>
                        </div>
                        <select name="id_enseignant"
                                class="text-sm text-[#0f2744] bg-slate-50 border border-black/8 rounded-lg pl-9 pr-8 py-2 outline-none focus:border-blue-500 focus:bg-white transition-colors appearance-none cursor-pointer min-w-44">
                            <option value="">Tous les enseignants</option>
                            <?php foreach ($enseignants as $ens): ?>
                                <option value="<?= $ens['id_enseignant'] ?>"
                                    <?= ($filtre_enseignant ?? '') == $ens['id_enseignant'] ? 'selected' : '' ?>>
                                    <?= htmlspecialchars($ens['nom'] . ' ' . $ens['prenom']) ?>
                                </option>
                            <?php endforeach; ?>
                        </select>
                        <div class="absolute inset-y-0 right-2.5 flex items-center pointer-events-none">
                            <svg width="12" height="12" fill="none" viewBox="0 0 24 24">
                                <polyline points="6 9 12 15 18 9" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </div>
                    </div>

                    <!-- Séparateur vertical -->
                    <div class="hidden sm:block w-px h-8 bg-black/8 shrink-0"></div>

                    <!-- Bouton soumettre -->
                    <button type="submit"
                            class="inline-flex items-center justify-center gap-2 px-4 py-2 bg-[#0f2744] hover:bg-[#1a3a5c] text-white text-sm font-medium rounded-lg transition-colors shrink-0">
                        <svg width="13" height="13" fill="none" viewBox="0 0 24 24">
                            <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
                            <line x1="21" y1="21" x2="16.65" y2="16.65" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                        Filtrer
                    </button>

                    <!-- Réinitialiser -->
                    <?php if ($filtre !== 'tous' || !empty($recherche) || !empty($filtre_enseignant)): ?>
                        <a href="?filtre=tous"
                        class="inline-flex items-center justify-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-600 text-sm font-medium rounded-lg transition-colors shrink-0">
                            <svg width="13" height="13" fill="none" viewBox="0 0 24 24">
                                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                            </svg>
                            Réinitialiser
                        </a>
                    <?php endif; ?>

                </div>

                <!-- Bande inférieure : résultats + filtres actifs -->
                <?php $hasFilters = !empty($recherche) || !empty($filtre_enseignant) || $filtre !== 'tous'; ?>
                <?php if ($hasFilters): ?>
                    <div class="flex items-center gap-2 px-3 pb-3 flex-wrap">
                        <span class="text-xs text-slate-400">Filtres actifs :</span>

                        <?php if (!empty($recherche)): ?>
                            <span class="inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 bg-blue-50 text-blue-700 rounded-full">
                                "<?= $t->e($recherche) ?>"
                            </span>
                        <?php endif; ?>

                        <?php if (!empty($filtre_enseignant)): ?>
                            <?php $nomEns = ''; foreach ($enseignants as $e) { if ($e['id_enseignant'] == $filtre_enseignant) { $nomEns = $e['nom'] . ' ' . $e['prenom']; break; } } ?>
                            <span class="inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 bg-purple-50 text-purple-700 rounded-full">
                                <?= htmlspecialchars($nomEns) ?>
                            </span>
                        <?php endif; ?>

                        <span class="ml-auto text-xs text-slate-400">
                            <?= count($liste) ?> résultat<?= count($liste) > 1 ? 's' : '' ?>
                        </span>
                    </div>
                <?php else: ?>
                    <div class="flex items-center justify-end px-3 pb-3">
                        <span class="text-xs text-slate-400">
                            <?= count($liste) ?> résultat<?= count($liste) > 1 ? 's' : '' ?>
                        </span>
                    </div>
                <?php endif; ?>

            </form>
        </div>
