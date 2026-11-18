// ESLint sur le JavaScript de web/ : pnpm --dir web lint
import js from '@eslint/js';
import globals from 'globals';

// Les bibliothèques chargées par <script> dans les pages PHP.
const PAGE_LIBRARIES = {
    L: 'readonly',
    Chart: 'readonly',
    ChartDataLabels: 'readonly',
    gantt: 'readonly',
    google: 'readonly',
};

// dependance_module/ : scripts classiques qui partagent leurs variables de haut niveau, et les
// constantes que la page PHP (views/dashboard/dependance_module.php) écrit avant eux.
const DEPENDANCE_MODULE_SHARED = {
    token: 'readonly',
    userId: 'readonly',
    userType: 'readonly',
    dataGantt: 'readonly',
    activeFilters: 'readonly',
    allTasksData: 'writable',
    ganttInitialized: 'writable',
    tagsContainer: 'writable',
    transformDataForDHTMLX: 'readonly',
    updateGanttChart: 'readonly',
    initDependanceFilters: 'readonly',
};

export default [
    { ignores: ['vendor/**', 'node_modules/**'] },
    js.configs.recommended,
    {
        files: ['**/*.js'],
        languageOptions: {
            sourceType: 'module',
            globals: { ...globals.browser, ...PAGE_LIBRARIES },
        },
        rules: {
            // Dette : des catch qui ignorent l'erreur ([EXCEPTIONS]), à rendre puis passer à "all".
            'no-unused-vars': ['error', { caughtErrors: 'none' }],
        },
    },
    {
        // Scripts classiques : leurs déclarations de haut niveau servent aux autres scripts et aux
        // attributs onclick de la page.
        files: ['scripts/liste_personnel.js', 'scripts/dependance_module/**/*.js', 'theme/**/*.js'],
        languageOptions: { sourceType: 'script' },
        rules: {
            'no-unused-vars': ['error', { vars: 'local', caughtErrors: 'none' }],
        },
    },
    {
        files: ['scripts/dependance_module/**/*.js'],
        languageOptions: { globals: DEPENDANCE_MODULE_SHARED },
        rules: { 'no-redeclare': ['error', { builtinGlobals: false }] },
    },
    {
        files: ['eslint.config.js', 'tests/**/*.mjs'],
        languageOptions: { globals: globals.node },
    },
];
