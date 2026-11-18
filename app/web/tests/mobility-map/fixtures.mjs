// Données fictives servies par l'API simulée du harnais des cartes de mobilité.

// La valeur de départ des filtres de la page.
export const INITIAL_VALUES = {
    semestreSelect: 'Tous',
    filiereSelect: 'Toutes',
    noteMinRange: '20',
};

// Les routes du backend ouvertes sans connexion.
export const AUTH_FREE_PATHS = ['university'];

const UNIVERSITIES = [
    {
        id_partner_university: 1, name: 'Université A', code: 'UA', address: '1 rue A', country: 'Pays A',
        languages: 'Anglais', annee: 4, number_of_places: 2, note_min: null, website: 'https://a.example.org',
        latitude: 10, longitude: 20, S8_total_places: 2, S9_total_places: 0,
    },
    {
        id_partner_university: 2, name: 'Université B', code: 'UB', address: '2 rue B', country: 'Pays B',
        languages: 'Espagnol', annee: 5, number_of_places: 1, note_min: '12', website: 'https://b.example.org',
        latitude: 30, longitude: 40, S8_total_places: 0, S9_total_places: 1,
    },
];

const WISHES = [
    { id_partner_university: 2, id_semestre: 9, priority: 1, name: 'Université B', code: 'UB', country: 'Pays B' },
];

// Réponse de chaque route, l'identifiant de l'étudiant remplacé par ID.
export const API_RESPONSES = {
    'university': UNIVERSITIES,
    'university/etudiant/ID/wishes': WISHES,
    'university/etudiant/ID/campaign-status': { is_open: true },
};
