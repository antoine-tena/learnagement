    <div id="mapSection" class="relative rounded-2xl border overflow-hidden h-[36rem]">
        <div id="map" class="absolute inset-0" style="height: 100%; width: 100%;"></div>

        <div class="absolute top-[10px] left-[55px] z-[1000] flex max-w-[92vw] flex-col items-start gap-2.5">
            <div class="flex items-center gap-2">
                <button onclick="document.getElementById('filterForm').classList.toggle('hidden')"
                    class="bg-white hover:bg-gray-100 text-gray-800 font-semibold py-2 px-4 border border-gray-400 rounded shadow text-sm">
                    Filtres carte
                </button>
            </div>

            <form id="filterForm" onsubmit="return false;"
                class="hidden bg-white p-4 rounded-lg shadow-lg border border-gray-200">
                <div class="flex flex-wrap justify-center items-center gap-4">
                    <div class="flex flex-col">
                        <label for="semestreSelect" class="text-xs font-semibold text-gray-600 mb-1">Semestre</label>
                        <select name="semestre" id="semestreSelect" onchange="updateMap()"
                            class="border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-primary min-w-24">
                            <option value="Tous">Tous</option>
                            <option value="S8">S8</option>
                            <option value="S9">S9</option>
                        </select>
                    </div>
                    <div class="flex flex-col">
                        <label for="filiereSelect" class="text-xs font-semibold text-gray-600 mb-1">Filiere</label>
                        <select name="filiere" id="filiereSelect" onchange="updateMap()"
                            class="border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-primary min-w-48">
                            <option value="toutes">Toutes</option>
                        </select>
                    </div>
                    <div class="flex flex-col">
                        <div class="flex justify-between items-center mb-1">
                            <label for="noteMinRange" class="text-xs font-semibold text-gray-600">Note minimale</label>
                            <span id="noteMinValue" class="text-xs font-bold text-gray-700">20</span>
                        </div>
                        <input type="range" name="notemin" id="noteMinRange" min="0" max="20" value="20"
                            class="w-32 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary"
                            oninput="document.getElementById('noteMinValue').innerText = this.value; updateMap()">
                    </div>
                </div>
            </form>
        </div>
    </div>

    <div id="streetViewModal" class="streetview-modal">
        <div class="streetview-content">
            <div class="streetview-header">
                <h2 id="streetViewTitle" class="text-lg font-semibold"></h2>
                <button class="streetview-close" onclick="window.closeStreetViewModal()">x</button>
            </div>
            <div id="streetViewPanoramaModal" style="width: 100%; height: 100%;"></div>
        </div>
    </div>
