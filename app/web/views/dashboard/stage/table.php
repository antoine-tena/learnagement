        <!-- Tableau -->
        <div class="rounded-2xl border overflow-hidden">
            <div class="overflow-x-auto">
                <table class="w-full text-sm text-left">
                    <thead class="text-xs uppercase border-b bg-primary text-on-primary">
                        <tr>
                            <th class="px-6 py-4 font-semibold">Étudiant</th>
                            <th class="px-6 py-4 font-semibold">Programme</th>
                            <th class="px-6 py-4 font-semibold">Statut</th>
                            <th class="px-6 py-4 font-semibold">Entreprise</th>
                            <th class="px-6 py-4 font-semibold">Intitulé</th>
                            <th class="px-6 py-4 font-semibold">Période</th>
                            <th class="px-6 py-4 font-semibold">Tuteur</th>
                            <th class="px-6 py-4 font-semibold text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-500">
                        <?php if (empty($liste)): ?>
                        <tr>
                            <td colspan="7" class="px-6 py-16 text-center">
                                <div class="flex flex-col items-center gap-3 text-gray-500">
                                    <svg class="w-12 h-12" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                                    <p class="font-medium">Aucun étudiant trouvé</p>
                                </div>
                            </td>
                        </tr>
                        <?php else: foreach ($liste as $e):
                            $badgeClass = match($e['status']) {
                                'no-internship'  => 'bg-red-100 text-red-700',
                                'pending' => 'bg-yellow-100 text-yellow-700',
                                'completed'     => 'bg-green-100 text-green-700',
                                default       => '',
                            };
                            $badgeLabel = match($e['status']) {
                                'no-internship'  => 'Sans stage',
                                'pending' => 'Sans tuteur',
                                'completed'     => 'Complet',
                                default       => '',
                            };
                            $mots = explode(' ', $e['student_fullname']);
                            $initiales = implode('', array_map(fn($w) => strtoupper($w[0]), $mots));
                        ?>
                        <tr class="hover:bg-gray-100 transition">

                            <td class="px-6 py-4">
                                <div class="flex items-center gap-3">
                                    <div class="w-9 h-9 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
                                        <span class="text-xs font-bold text-blue-600"><?= $t->e($initiales) ?></span>
                                    </div>
                                    <div>
                                        <div class="font-semibold text-gray-900"><?= $t->e($e['student_fullname']) ?></div>
                                        <div class="text-xs text-gray-500"><?= $t->e($e['mail']) ?></div>
                                    </div>
                                </div>
                            </td>

                            <td class="px-6 py-4 whitespace-nowrap text-gray-600"><?= $t->e($e['filiere']) ?></td>

                            <td class="px-6 py-4">
                                <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold <?= $badgeClass ?>">
                                    <?= $badgeLabel ?>
                                </span>
                            </td>

                            <td class="px-6 py-4">
                                <?php if ($e['entreprise']): ?>
                                    <div class="font-medium text-gray-900"><?= $t->e($e['entreprise']) ?></div>
                                    <div class="text-xs text-gray-500"><?= $t->e($e['nature']) ?></div>
                                <?php else: ?>
                                    <span class="text-gray-400">—</span>
                                <?php endif; ?>
                            </td>

                            <td class="px-6 py-4">
                                <?php if ($e['entreprise']): ?>
                                    <div class="font-medium text-gray-900"><?= $t->e($e['intitulé']) ?></div>
                                    <div class="text-xs text-gray-500"><?= $t->e($e['nature']) ?></div>
                                <?php else: ?>
                                    <span class="text-gray-400">—</span>
                                <?php endif; ?>
                            </td>

                            <td class="px-6 py-4 whitespace-nowrap">
                                <?php if ($e['entreprise']): ?>
                                    <div class="text-gray-900"><?= date('d/m/Y', strtotime($e['date_debut'])) ?></div>
                                    <div class="text-xs text-gray-500">→ <?= date('d/m/Y', strtotime($e['date_fin'])) ?></div>
                                <?php else: ?>
                                    <span class="text-gray-400">—</span>
                                <?php endif; ?>
                            </td>

                            <td class="px-6 py-4">
                                <?php if ($e['teacher_fullname']): ?>
                                    <div class="font-medium text-gray-900"><?= $t->e($e['teacher_fullname']) ?></div>
                                    <div class="text-xs text-gray-500"><?= $t->e($e['teacher_mail']) ?></div>
                                <?php elseif ($e['entreprise']): ?>
                                    <span class="inline-flex items-center gap-1 text-xs text-yellow-600 font-medium">
                                        <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>
                                        À assigner
                                    </span>
                                <?php else: ?>
                                    <span class="text-gray-500">—</span>
                                <?php endif; ?>
                            </td>

                            <td class="px-6 py-4">
                                <div class="flex items-center justify-end gap-2">
                                    <?php if ($user['type'] === 'administratif'): ?>
                                        <?php if ($e['entreprise']): ?>
                                            <button
                                                data-modal-target="modal-<?= $e['id_etudiant'] ?>"
                                                data-modal-toggle="modal-<?= $e['id_etudiant'] ?>"
                                                class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-50 rounded-lg hover:bg-blue-100 transition"
                                            >
                                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                                                Modifier
                                            </button>
                                        <?php else: ?>
                                            <a href="<?= $t->router->href('dashboard-create-stage', query: ['id_etudiant' => $e['id_etudiant']]) ?>"
                                                class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-green-700 bg-green-50 rounded-lg hover:bg-green-100 transition">
                                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
                                                Ajouter stage
                                            </a>
                                        <?php endif; ?>
                                    <?php else: ?>
                                        <?php if ($e['entreprise']): ?>
                                            <form action="<?= $t->router->href("dashboard-stage-post") ?>" method="POST">
                                                <input type="hidden" name="id_stage" value="<?= $t->e($e['id_stage'] ?? '') ?>">
                                                <input type="hidden" name="entreprise" value="<?= $t->e($e['entreprise'] ?? '') ?>">
                                                <input type="hidden" name="intitulé" value="<?= $t->e($e['intitulé'] ?? '') ?>">
                                                <input type="hidden" name="nature" value="<?= $t->e($e['nature'] ?? '') ?>">
                                                <input type="hidden" name="date_debut" value="<?= $t->e($e['date_debut'] ?? '') ?>">
                                                <input type="hidden" name="date_fin" value="<?= $t->e($e['date_fin'] ?? '') ?>">
                                                <input type="hidden" name="description" value="<?= $t->e($e['description'] ?? '') ?>">
                                                <input type="hidden" name="adresse" value="<?= $t->e($e['adresse'] ?? '') ?>">
                                                <input type="hidden" name="code_postal" value="<?= $t->e($e['code_postal'] ?? '') ?>">
                                                <input type="hidden" name="ville" value="<?= $t->e($e['ville'] ?? '') ?>">
                                                <input type="hidden" name="pays" value="<?= $t->e($e['pays'] ?? '') ?>">
                                                <input type="hidden" name="id_etudiant" value="<?= $t->e($e['id_etudiant'] ?? '') ?>">
                                                <input type="hidden" name="id_enseignant" value="<?= $user['id'] === $e['id_enseignant'] ? '' : $t->e($user['id']) ?>">

                                                <button type="submit"
                                                    class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg hover:bg-blue-100 transition
                                                    <?= $user['id'] === $e['id_enseignant'] ? 'text-red-700 bg-red-50' : 'text-blue-700 bg-blue-50' ?>">
                                                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                                                    <?= $user['id'] === $e['id_enseignant'] ? 'Retirer' : 'Remplacer' ?> tuteur
                                                </button>
                                            </form>
                                        <?php endif; ?>
                                        <button
                                            data-modal-target="modal-<?= $e['id_etudiant'] ?>"
                                            data-modal-toggle="modal-<?= $e['id_etudiant'] ?>"
                                            class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-700 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                                        >
                                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-3.5 h-3.5">
                                                <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                                                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                                            </svg>
                                            Détail
                                        </button>
                                    <?php endif; ?>
                                </div>
                            </td>

                        </tr>
                        <?php endforeach; endif; ?>
                    </tbody>
                </table>
            </div>
        </div>
