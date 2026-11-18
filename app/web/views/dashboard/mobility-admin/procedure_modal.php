    <!-- Procedure Modal -->
    <div id="procedureModal"
        class="hidden fixed inset-0 bg-gray-900 bg-opacity-50 z-[2000] flex items-center justify-center">
        <div class="bg-white rounded-xl shadow-xl w-full max-w-[90vw] xl:max-w-7xl p-6 max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-start mb-6">
                <h3 class="text-xl font-bold text-gray-900 flex items-center gap-2">
                    <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" stroke-width="2"
                        viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round"
                            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Centre de Contrôle : Mobilité
                </h3>
                <button onclick="document.getElementById('procedureModal').classList.add('hidden')"
                    class="text-gray-400 hover:text-gray-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12">
                        </path>
                    </svg>
                </button>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-0">
                <!-- COLONNE 1 -->
                <div class="space-y-6 lg:border-r lg:border-gray-200 lg:pr-8">

                    <!-- ETAPE 1 (Refonte) -->
                    <div class="mb-8">
                        <h4
                            class="text-sm font-bold text-gray-800 uppercase tracking-wide mb-2 flex items-center gap-2">
                            <span class="bg-gray-200 text-gray-700 px-2 py-0.5 rounded text-xs">Étape 1</span>
                            Préparation et Lancement de la Campagne
                        </h4>

                        <div class="grid grid-cols-1 gap-3">
                            <!-- Bouton 1 -->
                            <button onclick="document.getElementById('quotasModal').classList.remove('hidden')" class="w-full flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-50 hover:border-indigo-300 transition text-left group">
                                <div>
                                    <h5 class="font-bold text-gray-800 group-hover:text-indigo-700 transition">Gestion des Quotas</h5>
                                    <p class="text-xs text-gray-500 mt-1">Définir le nombre de places pour chaque filière avant le lancement.</p>
                                </div>
                                <svg class="w-6 h-6 text-gray-400 group-hover:text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                            </button>

                            <!-- Bouton 2 -->
                            <button onclick="document.getElementById('campaignModal').classList.remove('hidden')" class="w-full flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-50 hover:border-green-300 transition text-left group">
                                <div>
                                    <h5 class="font-bold text-gray-800 group-hover:text-green-700 transition">Lancement de la campagne & Redoublants</h5>
                                    <p class="text-xs text-gray-500 mt-1">Gérer les étudiants doublants et ouvrir la campagne de mobilité.</p>
                                </div>
                                <svg class="w-6 h-6 text-gray-400 group-hover:text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                            </button>

                            <!-- Bouton 3 -->
                            <button onclick="window.forceSubmitWishesUI()"
                                class="w-full mt-2 px-4 py-3 bg-red-600 text-white rounded-lg shadow-sm text-sm font-bold hover:bg-red-700 transition flex justify-center items-center gap-2">
                                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                                Clôturer l'étape 1 (Fermer les soumissions)
                            </button>
                        </div>
                    </div>

                    <hr class="border-gray-200">

                    <!-- ETAPE 2 -->
                    <div>
                        <h4
                            class="text-sm font-bold text-gray-800 uppercase tracking-wide mb-2 flex items-center gap-2">
                            <span class="bg-gray-200 text-gray-700 px-2 py-0.5 rounded text-xs">Étape 2</span>
                            Exécution de l'algorithme
                        </h4>

                        <div class="p-4 bg-gray-50 rounded-lg border border-gray-100 mb-4">
                            <p class="text-xs font-bold text-gray-800 mb-3">L'algorithme utilisera les quotas définis à l'Étape 1 pour répartir les étudiants de 4ème année sur les semestres S8 ou S9 des universités partenaires.</p>

                            <div class="mt-4 flex flex-col gap-4">
                                <div id="assignmentActions">
                                    <button onclick="window.runAssignmentUI()"
                                        class="w-full inline-flex justify-center items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition">
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
                                        Lancer l'affectation automatique
                                    </button>
                                </div>

                                <div id="assignmentProgressContainer" class="hidden w-full p-4 bg-white border border-gray-200 rounded-lg shadow-sm">
                                    <div class="flex justify-between text-xs font-semibold text-gray-700 mb-2">
                                        <span id="assignmentProgressText">Démarrage...</span>
                                        <span id="assignmentProgressPercent">0%</span>
                                    </div>
                                    <div class="w-full bg-gray-200 rounded-full h-2.5">
                                        <div id="assignmentProgressBar" class="bg-blue-600 h-2.5 rounded-full transition-all duration-300" style="width: 0%"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- COLONNE 2 -->
                <div class="space-y-6 lg:pl-8">
                    <!-- ETAPE 3 -->
                    <div>
                        <h4
                            class="text-sm font-bold text-gray-800 uppercase tracking-wide mb-2 flex items-center gap-2">
                            <span class="bg-gray-200 text-gray-700 px-2 py-0.5 rounded text-xs">Étape 3</span>
                            Validation manuelle des affectations
                        </h4>
                        <p class="text-xs text-gray-500 mb-3">Modifiez manuellement le statut d'un étudiant s'il vous
                            confirme sa décision en personne.</p>

                        <div class="mb-4">
                            <!-- Graphe et Export -->
                            <div
                                class="bg-gray-50 border rounded-xl p-4 shadow-sm flex flex-col items-center justify-center">
                                <h4 class="font-bold text-gray-700 mb-2 text-center text-sm">Statut des Affectations
                                </h4>
                                <div class="w-full relative h-40 flex justify-center">
                                    <canvas id="chartEtape3Status"></canvas>
                                </div>
                                <div
                                    class="mt-4 flex gap-3 text-[11px] font-semibold text-indigo-600 flex-wrap justify-center">
                                    <a href="#" onclick="exportAssignedData('accepted')"
                                        class="hover:underline flex items-center gap-1"><svg class="w-3 h-3" fill="none"
                                            stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-3 3m0 0l-3-3m3 3V4" />
                                        </svg> Acceptés</a>
                                    <a href="#" onclick="exportAssignedData('pending')"
                                        class="hover:underline flex items-center gap-1"><svg class="w-3 h-3" fill="none"
                                            stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-3 3m0 0l-3-3m3 3V4" />
                                        </svg> En attente</a>
                                    <a href="#" onclick="exportAssignedData('declined')"
                                        class="hover:underline flex items-center gap-1"><svg class="w-3 h-3" fill="none"
                                            stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-3 3m0 0l-3-3m3 3V4" />
                                        </svg> Refusés</a>
                                    <a href="#" onclick="exportUnassignedData()"
                                        class="hover:underline flex items-center gap-1 text-red-600"><svg class="w-3 h-3" fill="none"
                                            stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-3 3m0 0l-3-3m3 3V4" />
                                        </svg> Non affectés</a>
                                </div>
                            </div>
                        </div>

                        <!-- Bouton Cloture Phase d'acceptation deplace a la fin de l'etape 3 -->
                        <div class="mt-4 flex justify-center">
                            <button onclick="window.closeAssignmentPhase()"
                                class="px-4 py-2 bg-red-600 text-white rounded-lg shadow-sm text-sm font-bold hover:bg-red-700 transition">
                                Clôture de la phase d'acceptation
                            </button>
                        </div>
                    </div>

                    <hr class="border-gray-200">

                    <!-- ETAPE 4 -->
                    <div>
                        <h4
                            class="text-sm font-bold text-gray-800 uppercase tracking-wide mb-2 flex items-center gap-2">
                            <span class="bg-gray-200 text-gray-700 px-2 py-0.5 rounded text-xs">Étape 4</span>
                            Exportation des Résultats
                        </h4>
                        <p class="text-xs text-gray-500 mb-3">Téléchargez les listes finales pour communication aux
                            universités partenaires.</p>
                        <div class="flex gap-3">
                            <button onclick="exportWishes()"
                                class="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-green-700 bg-green-100 rounded-lg hover:bg-green-200 transition">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2"
                                    viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round"
                                        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                </svg>
                                Vœux (XLSX)
                            </button>
                            <button onclick="exportAssignments()"
                                class="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-green-700 bg-green-100 rounded-lg hover:bg-green-200 transition">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2"
                                    viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round"
                                        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                </svg>
                                Affectations (XLSX)
                            </button>
                            <button onclick="exportPlaces()"
                                class="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-green-700 bg-green-100 rounded-lg hover:bg-green-200 transition">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2"
                                    viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round"
                                        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                </svg>
                                État des places (XLSX)
                            </button>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </div>
