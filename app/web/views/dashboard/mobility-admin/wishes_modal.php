    <!-- Wishes Modal -->
    <div id="wishesModal" class="hidden fixed inset-0 bg-gray-900 bg-opacity-50 z-[2000] flex items-center justify-center p-4">
        <div class="bg-white rounded-xl shadow-xl w-full max-w-[95vw] p-6 max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-start mb-6">
                <h3 class="text-xl font-bold text-gray-900 flex items-center gap-2">
                    <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                    </svg>
                    Liste des Vœux Étudiants
                </h3>
                <button onclick="window.toggleWishesModal()" class="text-gray-400 hover:text-gray-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>

            <div class="rounded-2xl border mb-6">
                <div class="p-4 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
                    <div class="relative w-full lg:w-96">
                        <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round"
                                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                        </div>
                        <input id="wishesSearch" type="search" placeholder="Rechercher un étudiant, email ou université..."
                            class="border text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 p-2.5" />
                    </div>
                    <div class="flex flex-wrap items-center gap-3">
                        <label for="wishesFiliereFilter"
                            class="text-xs font-semibold uppercase tracking-wide text-gray-500">Filière</label>
                        <select id="wishesFiliereFilter" class="border border-gray-300 rounded-lg px-3 py-2 text-sm min-w-[150px]">
                            <option value="toutes">Toutes</option>
                        </select>
                        <div class="h-6 w-px bg-gray-300 mx-1 hidden sm:block"></div>
                        <label for="dossierStatusFilter"
                            class="text-xs font-semibold uppercase tracking-wide text-blue-600 bg-blue-50 px-2 py-1 rounded">Phase 1: Soumission</label>
                        <select id="dossierStatusFilter" class="border border-blue-300 bg-blue-50/30 rounded-lg px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500 min-w-[150px]">
                            <option value="tous">Tous</option>
                            <option value="complet">Complet</option>
                            <option value="incomplet">Incomplet</option>
                            <option value="retardataire">Retardataire</option>
                        </select>
                        <div class="h-6 w-px bg-gray-300 mx-1 hidden sm:block"></div>
                        <label for="assignmentStatusFilter"
                            class="text-xs font-semibold uppercase tracking-wide text-purple-600 bg-purple-50 px-2 py-1 rounded">Phase 3: Acceptation</label>
                        <select id="assignmentStatusFilter" class="border border-purple-300 bg-purple-50/30 rounded-lg px-3 py-2 text-sm focus:ring-purple-500 focus:border-purple-500 min-w-[150px]">
                            <option value="tous">Tous</option>
                            <option value="accepted">Accepté</option>
                            <option value="declined">Refusé</option>
                            <option value="pending">En attente</option>
                            <option value="none">Non affecté</option>
                        </select>
                        <button id="resetDashboardFilters" type="button"
                            class="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 transition">
                            Réinitialiser
                        </button>
                        <span id="wishesResultsCount" class="text-sm">0 résultat</span>
                    </div>
                </div>
            </div>

            <div class="rounded-2xl border overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="w-full text-sm text-left">
                        <thead class="text-xs uppercase border-b bg-primary text-on-primary">
                            <tr>
                                <th class="px-6 py-4 font-semibold">Étudiant</th>
                                <th class="px-6 py-4 font-semibold">N° Étudiant</th>
                                <th class="px-6 py-4 font-semibold">Filière</th>
                                <th class="px-6 py-4 font-semibold">Date soumission</th>
                                <th class="px-6 py-4 font-semibold">Statut de soumission</th>
                                <th class="px-6 py-4 font-semibold">Nombre de vœux</th>
                                <th class="px-6 py-4 font-semibold">Acceptation</th>
                                <th class="px-6 py-4 font-semibold text-right">Détails</th>
                            </tr>
                        </thead>
                        <tbody id="wishesTableBody" class="divide-y divide-gray-200">
                            <tr>
                                <td colspan="8" class="px-6 py-12 text-center text-gray-500">Chargement des dossiers...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
