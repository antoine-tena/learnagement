// ==========================================
// INITIALISATION ET CONFIGURATION DE DHTMLX
// ==========================================

function updateGanttChart(tasksData) {
    const ganttContainer = document.getElementById('gantt-chart');

    if (!tasksData || tasksData.data.length === 0) {
        ganttContainer.innerHTML = "<p style='color: gray; padding: 20px;'>Aucune donnée trouvée.</p>";
        ganttInitialized = false;
        return;
    }

    // ── Configuration (toujours avant init) ──────────────────────
    gantt.config.date_format = "%Y-%m-%d";
    gantt.config.readonly = true;
    gantt.config.scale_unit = "month";
    gantt.config.date_scale = "%M %Y";
    gantt.config.min_column_width = 70;

    gantt.config.columns = [{
        name: "text",
        label: "Détails du module",
        width: "200",
        tree: true,
        template: function(task) {
            if (task.is_group) {
                return `<strong style="color:#2c3e50; font-size:1.1em;">📁 ${task.text}</strong>`;
            }
            const code = task.code_module || "N/A";
            const duree = task.duree_h ? `${task.duree_h}h` : "";
            const typeBadge = task.type ? `<span class="badge-type">${task.type}</span>` : "";
            return `
                <div style="display: flex; align-items: center; gap: 8px;">
                    <strong>${code}</strong>
                    <span style="color: gray; font-size: 0.85em;">${duree}</span>
                    ${typeBadge}
                </div>`;
        }
    }];

    // ── Init une seule fois ───────────────────────────────────────
    if (!ganttInitialized) {
        ganttContainer.innerHTML = ""; // on vide uniquement avant le premier init
        gantt.init("gantt-chart");
        const observer = new ResizeObserver(() => gantt.setSizes());
        observer.observe(ganttContainer);
        ganttInitialized = true;
    }

    // ── Toujours clearAll + parse pour rafraîchir ─────────────────
    gantt.clearAll();

    // ── Construction de l'arbre ───────────────────────────────────
    const treeData = [];
    const processedModules = new Set();

    tasksData.data.forEach(task => {
        const moduleCode = task.code_module;

        if (moduleCode && !processedModules.has(moduleCode)) {
            treeData.push({
                id: `group_${moduleCode}`,
                text: `${moduleCode} (${task.name || "Module"  })`,
                is_group: true,
                open: true,
                type: gantt.config.types.project
            });
            processedModules.add(moduleCode);
        }

        if (moduleCode) task.parent = `group_${moduleCode}`;
        treeData.push(task);
    });

    tasksData.data = treeData;
    gantt.parse(tasksData);
}
