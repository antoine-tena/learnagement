    <div class="rounded-2xl border overflow-hidden">
        <div class="p-4 border-b flex flex-col lg:flex-row gap-3 lg:items-center lg:justify-between">
            <div>
                <h2 class="text-lg font-bold">Universités partenaires</h2>
                <p class="text-sm text-gray-500">Ajout et ajustement des places par filière/semestre.</p>
            </div>
            <div class="flex flex-wrap items-center gap-2">
                <input id="universityAdminSearch" type="search" placeholder="Rechercher une universite..."
                    class="border text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-64 p-2.5" />
                <button id="addUniversityRowBtn" type="button"
                    class="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 transition">
                    Ajouter une universite
                </button>
            </div>
        </div>
        <div id="addUniversityPanel" class="hidden p-4 border-b bg-gray-50">
            <div class="mb-3 flex items-center justify-between">
                <h3 class="text-sm font-semibold text-gray-800">Nouvelle université partenaire</h3>
                <button id="cancelAddUniversityBtn" type="button"
                    class="text-xs px-3 py-1.5 rounded bg-gray-200 text-gray-700 hover:bg-gray-300">Annuler</button>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-3 mb-3">
                <input id="newUniName" type="text" placeholder="Nom de l'université *"
                    class="border rounded px-3 py-2 text-sm" />
                <input id="newUniCountry" type="text" placeholder="Pays *" class="border rounded px-3 py-2 text-sm" />
                <input id="newUniCode" type="text" placeholder="Code" class="border rounded px-3 py-2 text-sm" />
                <input id="newUniAddress" type="text" placeholder="Adresse"
                    class="border rounded px-3 py-2 text-sm lg:col-span-2" />
                <input id="newUniWebsite" type="url" placeholder="Site web" class="border rounded px-3 py-2 text-sm" />
                <input id="newUniLanguages" type="text" placeholder="Langues (ex: Anglais, Espagnol)"
                    class="border rounded px-3 py-2 text-sm lg:col-span-2" />
                <div class="grid grid-cols-3 gap-2 lg:col-span-1">
                    <input id="newUniLatitude" type="number" step="0.000001" placeholder="Latitude"
                        class="border rounded px-3 py-2 text-sm" />
                    <input id="newUniLongitude" type="number" step="0.000001" placeholder="Longitude"
                        class="border rounded px-3 py-2 text-sm" />
                    <input id="newUniNoteMin" type="number" step="0.01" min="0" max="20" placeholder="Note min"
                        class="border rounded px-3 py-2 text-sm" />
                </div>
                <select id="newUniType" class="border rounded px-3 py-2 text-sm">
                    <option value="ERASMUS">ERASMUS</option>
                    <option value="Bilateral">Bilateral</option>
                </select>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
                <div class="rounded border bg-white p-3">
                    <h4 class="text-xs font-semibold uppercase tracking-wide text-gray-600 mb-2">Semestre 8 (S8)</h4>
                    <div class="mb-3">
                        <label class="text-[10px] uppercase font-semibold text-gray-500 mb-1 block">Places globales S8</label>
                        <input id="newUniS8Total" type="number" min="0" value="0" class="border rounded px-3 py-1.5 text-sm w-full" />
                    </div>
                    <div class="mb-2 flex items-center justify-between">
                        <span class="text-[10px] uppercase font-semibold text-gray-500">Places par filière (S8)</span>
                        <button type="button" class="text-xs px-2 py-1 rounded bg-gray-200 text-gray-700 hover:bg-gray-300" onclick="window.addNewUniversityPlaceRow(4, 'newUniPlacesRowsS8')">Ajouter une ligne</button>
                    </div>
                    <div id="newUniPlacesRowsS8" class="space-y-2"></div>
                </div>
                <div class="rounded border bg-white p-3">
                    <h4 class="text-xs font-semibold uppercase tracking-wide text-gray-600 mb-2">Semestre 9 (S9)</h4>
                    <div class="mb-3">
                        <label class="text-[10px] uppercase font-semibold text-gray-500 mb-1 block">Places globales S9</label>
                        <input id="newUniS9Total" type="number" min="0" value="0" class="border rounded px-3 py-1.5 text-sm w-full" />
                    </div>
                    <div class="mb-2 flex items-center justify-between">
                        <span class="text-[10px] uppercase font-semibold text-gray-500">Places par filière (S9)</span>
                        <button type="button" class="text-xs px-2 py-1 rounded bg-gray-200 text-gray-700 hover:bg-gray-300" onclick="window.addNewUniversityPlaceRow(5, 'newUniPlacesRowsS9')">Ajouter une ligne</button>
                    </div>
                    <div id="newUniPlacesRowsS9" class="space-y-2"></div>
                </div>
            </div>

            <div class="mt-3 flex items-center justify-end gap-2">
                <button id="saveNewUniversityBtn" type="button"
                    class="text-xs px-3 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700">Créer
                    l'université</button>
            </div>
        </div>
        <div class="overflow-x-auto">
            <table class="w-full text-sm text-left">
                <thead class="text-xs uppercase border-b bg-primary text-on-primary">
                    <tr>
                        <th class="px-6 py-4 font-semibold">Universite</th>
                        <th class="px-6 py-4 font-semibold">Pays</th>
                        <th class="px-6 py-4 font-semibold">Code</th>
                        <th class="px-6 py-4 font-semibold">Demandes</th>
                        <th class="px-6 py-4 font-semibold text-right">Actions</th>
                    </tr>
                </thead>
                <tbody id="universitiesAdminBody" class="divide-y divide-gray-500">
                    <tr>
                        <td colspan="5" class="px-6 py-10 text-center text-gray-500">Chargement des universites...</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
