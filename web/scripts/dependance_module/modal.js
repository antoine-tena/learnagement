document.addEventListener("DOMContentLoaded", () => {
    tagsContainer = document.getElementById('active-tags-container');
    const dropdowns = document.querySelectorAll('.select');
    const btnOpen = document.querySelector('.button-section button');
    const modal = document.getElementById('modal-ajout-module');
    const form = document.getElementById('form-ajout-module');
    const btnCancel_Cross = document.getElementById('btn-cancel-module-cross');
    const btnCancel = document.getElementById('btn-cancel-module');

   if (typeof dataGantt !== 'undefined') {
    allTasksData = transformDataForDHTMLX(dataGantt, userType); // ← stockage global
    updateGanttChart({ data: [...allTasksData.data], links: allTasksData.links });
    }
    else {
        console.error("Les données dataGantt ne sont pas définies.");
    }

    if (btnOpen && modal) {
        btnOpen.addEventListener('click', (e) => {
            e.preventDefault();
            modal.showModal();
        });
    }

    if (btnCancel && modal || (btnCancel_Cross && modal)) {
        btnCancel.addEventListener('click', () => {
            modal.close();
            form.reset();
        });
        btnCancel_Cross.addEventListener('click', () => {
            modal.close();
            form.reset();
        });
    }

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault(); // Empêche le rechargement de la page

            const formData = new FormData(form);
            console.log("Données du formulaire :", Object.fromEntries(formData.entries()));

            const payload = {
                code_module: formData.get('code_module'),
                nom: formData.get('nom_module'),
                hCM: parseFloat(formData.get('hCM')) || 0,
                hTD: parseFloat(formData.get('hTD')) || 0,
                hTP: parseFloat(formData.get('hTP')) || 0,
                hProj: parseFloat(formData.get('hProjet')) || 0,
                hPerso: parseFloat(formData.get('hPerso')) || 0,
                ECTS: parseFloat(formData.get('ECTS')) || 0,
                semestre: parseInt(formData.get('semestre')),
                id_responsable: parseInt(formData.get('id_responsable')),
                id_discipline: parseInt(formData.get('id_discipline'))
            };
            console.log("Payload à envoyer :", payload);

            try {
                const response = await fetch(window.location.href, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(payload)
                    });

                if (response.ok) {
                    const result = await response.json();
                    alert("Module créé avec succès !");
                    modal.close();
                    form.reset();
                    window.location.reload();
                } else {
                    const error = await response.json();
                    alert("Erreur lors de la création : " + (error.detail || response.statusText));
                }

            } catch (err) {
                console.error("Erreur de requête :", err);
                alert("Impossible de joindre le serveur.");
            }
        });
    }

    initDependanceFilters(dropdowns);
});
