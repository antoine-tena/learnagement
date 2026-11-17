    <div id="quotasModal" class="hidden fixed inset-0 bg-gray-900 bg-opacity-50 z-[2000] flex items-center justify-center p-4">
        <div class="bg-white rounded-xl shadow-xl w-full max-w-4xl p-6 max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-start mb-6">
                <h3 class="text-xl font-bold text-gray-900 flex items-center gap-2">
                    Gestion des Quotas de Mobilité
                </h3>
                <button onclick="document.getElementById('quotasModal').classList.add('hidden')" class="text-gray-400 hover:text-gray-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
            </div>

            <div class="mb-4">
                <p class="text-sm text-gray-600 mb-4">Définissez le nombre d'étudiants autorisés à partir pour chaque filière et semestre.</p>

                <div class="overflow-x-auto border border-gray-200 rounded-lg shadow-sm mb-6">
                    <table class="w-full text-sm text-left text-gray-700">
                        <thead class="text-xs uppercase bg-gray-50 text-gray-600 border-b border-gray-200">
                            <tr>
                                <th class="px-4 py-3 font-bold w-1/2">Filière</th>
                                <th class="px-4 py-3 font-bold text-center">Places S8</th>
                                <th class="px-4 py-3 font-bold text-center">Places S9</th>
                            </tr>
                        </thead>
                        <tbody id="quotasGridBody" class="divide-y divide-gray-100">
                            <tr>
                                <td colspan="3" class="px-4 py-8 text-center text-gray-400 italic">Chargement des filières...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="flex justify-end gap-3 pt-4 border-t border-gray-100">
                    <button onclick="document.getElementById('quotasModal').classList.add('hidden')" class="px-6 py-2 bg-white border border-gray-300 text-gray-700 font-semibold rounded-lg shadow-sm hover:bg-gray-50 transition">
                        Retour au Centre de Contrôle
                    </button>
                    <button onclick="window.saveMobilityQuotas()" class="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg shadow-sm transition flex items-center gap-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                        Enregistrer
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div id="campaignModal" class="hidden fixed inset-0 bg-gray-900 bg-opacity-50 z-[2000] flex items-center justify-center p-4">
        <div class="bg-white rounded-xl shadow-xl w-full max-w-7xl p-6 max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-start mb-6">
                <h3 class="text-xl font-bold text-gray-900 flex items-center gap-2">
                    Lancement de la campagne & Redoublants
                </h3>
                <button onclick="document.getElementById('campaignModal').classList.add('hidden')" class="text-gray-400 hover:text-gray-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
            </div>

            <div class="mb-4">
                <p class="text-sm font-bold text-gray-800 mb-3">Saisissez l'ID des étudiants doublants et leur Moyenne Centrée Réduite manuellement avant de lancer la campagne.</p>
                <div class="flex gap-2 mb-3">
                    <input type="number" id="doublantEtudiantId" placeholder="ID Étudiant" class="w-1/2 text-sm border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500">
                    <input type="number" step="0.01" id="doublantZScore" placeholder="Moyenne C. Réduite" class="w-1/2 text-sm border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500">
                </div>
                <button type="button" onclick="window.addDoublantToList()" class="mb-3 w-full inline-flex justify-center items-center gap-2 px-4 py-2 text-sm font-semibold text-blue-700 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition">Ajouter à la liste</button>

                <div class="flex justify-between items-center mb-2 mt-4 hidden" id="doublantsHeader">
                    <h5 class="text-sm font-bold text-gray-700">Liste des doublants ajoutés</h5>
                    <div class="flex items-center gap-2">
                        <div id="doublantsFiliereCounters" class="flex flex-wrap gap-2 justify-end"></div>
                        <span class="bg-gray-100 text-gray-800 text-xs font-bold px-2.5 py-1 rounded shadow-sm border border-gray-200" id="doublantsCount">0 total</span>
                    </div>
                </div>
                <ul id="doublantsList" class="text-sm text-gray-600 mb-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 max-h-[32rem] overflow-y-auto p-1"></ul>

                <hr class="border-gray-200 mb-6">

                <div id="campaignLaunchControls">
                    <button id="btnLaunchCampaign" onclick="window.launchCampaign()" class="w-full inline-flex justify-center items-center gap-2 px-4 py-3 text-sm font-semibold text-white bg-green-600 rounded-lg shadow hover:bg-green-700 transition">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path><path stroke-linecap="round" stroke-linejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        Ouvrir la campagne & Calculer les scores
                    </button>
                </div>

                <div id="campaignProgressContainer" class="hidden w-full mt-4 p-4 bg-white border border-gray-200 rounded-lg shadow-sm">
                    <div class="flex justify-between text-xs font-semibold text-gray-700 mb-2">
                        <span id="campaignProgressText">Lancement en cours...</span>
                        <span id="campaignProgressPercent">0%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2.5">
                        <div id="campaignProgressBar" class="bg-green-600 h-2.5 rounded-full transition-all duration-300" style="width: 0%"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div id="diagnosticsModal"
        class="hidden fixed inset-0 bg-gray-900 bg-opacity-50 z-[2000] flex items-center justify-center p-4">
        <div class="bg-white rounded-xl shadow-xl w-full max-w-5xl p-6 max-h-[95vh] overflow-y-auto">
            <div class="flex items-center justify-between mb-6">
                <h3 class="text-xl font-bold text-gray-900 flex items-center gap-2">
                    <svg class="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" stroke-width="2"
                        viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round"
                            d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
                        <path stroke-linecap="round" stroke-linejoin="round"
                            d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
                    </svg>
                    Diagnostique & Statistiques (Telling Story)
                </h3>
                <button onclick="document.getElementById('diagnosticsModal').classList.add('hidden')"
                    class="text-gray-400 hover:text-gray-600 transition">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <!-- Graphe 1 -->
                <div class="bg-gray-50 border rounded-xl p-4 shadow-sm flex flex-col items-center">
                    <h4 class="font-bold text-gray-700 mb-2 text-center text-sm">1. Statut Global de la Mobilité</h4>
                    <p class="text-xs text-gray-500 mb-4 text-center">La population totale de la promotion étudiée.</p>
                    <div class="w-full relative h-48 flex justify-center">
                        <canvas id="chartGlobalStatus"></canvas>
                    </div>
                    <div class="mt-4 flex gap-4 text-xs font-semibold text-indigo-600">
                        <a href="#" onclick="exportDiagnosticData('validated')"
                            class="hover:underline flex items-center gap-1"><svg class="w-3 h-3" fill="none"
                                stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-3 3m0 0l-3-3m3 3V4" />
                            </svg> Validés</a>
                        <a href="#" onclick="exportDiagnosticData('remaining')"
                            class="hover:underline flex items-center gap-1"><svg class="w-3 h-3" fill="none"
                                stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-3 3m0 0l-3-3m3 3V4" />
                            </svg> Non validés</a>
                    </div>
                </div>

                <!-- Graphe 2 -->
                <div class="bg-gray-50 border rounded-xl p-4 shadow-sm flex flex-col items-center">
                    <h4 class="font-bold text-gray-700 mb-2 text-center text-sm">2. Avancement des étudiants à traiter
                    </h4>
                    <p class="text-xs text-gray-500 mb-4 text-center">Ceux qui n'ont pas encore validé leur mobilité.
                    </p>
                    <div class="w-full relative h-48 flex justify-center">
                        <canvas id="chartWishesStatus"></canvas>
                    </div>
                    <div class="mt-4 flex gap-3 text-[11px] font-semibold text-indigo-600 flex-wrap justify-center">
                        <a href="#" onclick="exportDiagnosticData('submitted')"
                            class="hover:underline flex items-center gap-1"><svg class="w-3 h-3" fill="none"
                                stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-3 3m0 0l-3-3m3 3V4" />
                            </svg> Soumis</a>
                        <a href="#" onclick="exportDiagnosticData('in_progress')"
                            class="hover:underline flex items-center gap-1"><svg class="w-3 h-3" fill="none"
                                stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-3 3m0 0l-3-3m3 3V4" />
                            </svg> En cours</a>
                        <a href="#" onclick="exportDiagnosticData('retardataires')"
                            class="hover:underline flex items-center gap-1"><svg class="w-3 h-3" fill="none"
                                stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-3 3m0 0l-3-3m3 3V4" />
                            </svg> Retardataires</a>
                    </div>
                </div>

                <!-- Graphe 3 -->
                <div class="bg-gray-50 border rounded-xl p-4 shadow-sm flex flex-col items-center">
                    <h4 class="font-bold text-gray-700 mb-2 text-center text-sm">3. Nombre de choix effectués</h4>
                    <p class="text-xs text-gray-500 mb-4 text-center">Répartition du nombre de vœux enregistrés.</p>
                    <div class="w-full relative h-48 flex justify-center">
                        <canvas id="chartWishesDistribution"></canvas>
                    </div>
                </div>
            </div>

            <div class="mt-8 flex justify-end">
                <button onclick="document.getElementById('diagnosticsModal').classList.add('hidden')"
                    class="px-5 py-2 text-sm font-semibold text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-lg transition">Fermer</button>
            </div>
        </div>
    </div>
    <!-- Confirmation Code Modal -->
    <div id="confirmActionModal"
        class="hidden fixed inset-0 bg-gray-900 bg-opacity-75 z-[3000] flex items-center justify-center p-4">
        <div class="bg-white rounded-xl shadow-xl w-full max-w-sm p-6 text-center">
            <h3 class="text-lg font-bold text-red-600 mb-2">Action Critique</h3>
            <p class="text-sm text-gray-600 mb-4" id="confirmActionDescription"></p>

            <div class="bg-gray-100 p-3 rounded mb-4 font-mono text-xl tracking-[0.2em] font-bold text-gray-800 select-none"
                id="confirmActionCodeDisplay"></div>

            <p class="text-xs text-gray-500 mb-2">Veuillez recopier le code ci-dessus pour confirmer :</p>
            <input type="text" id="confirmActionCodeInput"
                class="w-full text-center text-lg font-mono border-gray-300 rounded focus:ring-red-500 focus:border-red-500 mb-4 uppercase"
                placeholder="Entrez le code" autocomplete="off">

            <div class="flex gap-3 justify-center">
                <button onclick="document.getElementById('confirmActionModal').classList.add('hidden')"
                    class="px-4 py-2 text-sm font-semibold text-gray-600 bg-gray-200 hover:bg-gray-300 rounded transition">Annuler</button>
                <button id="confirmActionButton"
                    class="px-4 py-2 text-sm font-semibold text-white bg-red-600 hover:bg-red-700 rounded transition opacity-50 cursor-not-allowed"
                    disabled>Confirmer</button>
            </div>
        </div>
    </div>
