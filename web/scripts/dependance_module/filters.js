function checkTaskMatchesFilter(task, filterId, values) {
    switch (filterId) {
        case 'filiere-filter': return values.includes(String(task.filiere));
        case 'periode-filter': return values.includes(String(task.semester));
        case 'module-filter':  return values.includes(String(task.name));
        case 'type-filter':    return values.includes(String(task.type));
        default: return true;
    }
}

function applyFiltersAndRefresh() {
    if (!allTasksData) return;

    let filteredTasks = allTasksData.data.filter(task => {
        for (const [filterId, filterValue] of Object.entries(activeFilters)) {
            if (!filterValue) continue;

            let values = [];
            if (filterValue instanceof Set && filterValue.size > 0) {
                values = Array.from(filterValue).map(f => f.value);
            } else if (filterValue.value) {
                values = [filterValue.value];
            }

            if (values.length > 0 && !checkTaskMatchesFilter(task, filterId, values)) {
                return false;
            }
        }
        return true;
    });

    const filteredIds = new Set(filteredTasks.map(t => t.id));
    const filteredLinks = allTasksData.links.filter(l =>
        filteredIds.has(l.source) && filteredIds.has(l.target)
    );

    updateGanttChart({ data: [...filteredTasks], links: filteredLinks });
}

function createTag(filterId, text, value) {
    const tag = document.createElement('div');
    tag.classList.add('filter-tag');
    tag.setAttribute('data-filter', filterId);
    tag.setAttribute('data-value', value);

    tag.innerHTML = `
        <span class="tag-text">${text}</span>
        <button class="remove-tag" aria-label="Supprimer le filtre">&times;</button>
    `;

    tag.querySelector('.remove-tag').addEventListener('click', function () {
        tag.remove();

        const isMultiple = (filterId === 'filiere-filter' || filterId === 'module-filter');
        if (isMultiple) {
            for (let item of activeFilters[filterId]) {
                if (item.value === value) {
                    activeFilters[filterId].delete(item);
                    break;
                }
            }
        } else {
            activeFilters[filterId] = null;
            const select = document.getElementById(filterId);
            if (select) select.value = "";
        }

        applyFiltersAndRefresh();
    });

    tagsContainer.appendChild(tag);

    applyFiltersAndRefresh();
}

function initDependanceFilters(dropdowns) {
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('change', function() {
            const filterId = this.id;
            const selectedText = this.options[this.selectedIndex].text;
            const selectedValue = this.value;
            console.log(`Sélection dans ${filterId} :`, { value: selectedValue, text: selectedText });

            if (selectedValue === "") return;

            const isMultiple = (filterId === 'filiere-filter' || filterId === 'module-filter');

            if (isMultiple) {
                if (!activeFilters[filterId]) {
                    activeFilters[filterId] = new Set();
                }

                let alreadyExists = Array.from(activeFilters[filterId]).some(item => item.value === selectedValue);

                if (!alreadyExists) {
                    activeFilters[filterId].add({ value: selectedValue, text: selectedText });
                    createTag(filterId, selectedText, selectedValue);
                }

                this.selectedIndex = 0;
            } else {
                activeFilters[filterId] = { value: selectedValue, text: selectedText };

                let existingTag = document.querySelector(`.filter-tag[data-filter="${filterId}"]`);

                if (existingTag) {
                    existingTag.querySelector('.tag-text').textContent = selectedText;
                    existingTag.setAttribute('data-value', selectedValue);
                    applyFiltersAndRefresh();
                } else {
                    createTag(filterId, selectedText, selectedValue);
                }
            }
        });
    });
}
