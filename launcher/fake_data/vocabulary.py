"""Les mots dont sont faites les données fictives : aucun ne désigne une personne réelle."""

from enum import StrEnum

FIRST_NAMES = (
    "Adèle", "Alix", "Amandine", "Antonin", "Armand", "Aurore", "Basile", "Bastien", "Bérénice",
    "Camille", "Capucine", "Célestin", "Clément", "Colette", "Constance", "Corentin", "Daphné",
    "Désiré", "Edgar", "Éloïse", "Émile", "Ernest", "Faustine", "Félicie", "Firmin", "Gaspard",
    "Gustave", "Hector", "Héloïse", "Honorine", "Ignace", "Isaure", "Jeanne", "Joachim", "Josèphe",
    "Léandre", "Léonie", "Lucien", "Lucille", "Mahaut", "Marcel", "Margaux", "Maxence", "Mélisande",
    "Noé", "Octave", "Odile", "Olympe", "Philémon", "Prosper", "Rosalie", "Sacha", "Salomé",
    "Séraphin", "Solène", "Théodore", "Tiphaine", "Ulysse", "Valentin", "Zélie",
)  # fmt: skip

LAST_NAMES = (
    "Aubépine", "Balsamine", "Bergamote", "Bourrache", "Bruyère", "Campanule", "Capucin",
    "Cardamome", "Cerfeuil", "Chicorée", "Ciboulette", "Coquelicot", "Coriandre", "Cyprès",
    "Dahlia", "Églantier", "Épicéa", "Fenouil", "Fougère", "Framboisier", "Frêne", "Gentiane",
    "Genêt", "Glycine", "Groseillier", "Hellébore", "Houx", "Jacinthe", "Jonquille", "Lavande",
    "Liseron", "Mélèze", "Mélisse", "Mimosa", "Muguet", "Myrtille", "Noisetier", "Œillet",
    "Orpin", "Pâquerette", "Pervenche", "Pissenlit", "Pivoine", "Primevère", "Prunellier",
    "Renoncule", "Romarin", "Roseau", "Sarriette", "Saule", "Serpolet", "Sorbier", "Sureau",
    "Tamaris", "Tilleul", "Trèfle", "Tulipe", "Verveine", "Violette", "Viorne",
)  # fmt: skip

COMPANIES = (
    "Alpes Logiciels", "Atelier Névé", "Bureau Cairn", "Capteurs du Lac", "Cimes Industrie",
    "Combe Énergie", "Crêtes Data", "Fruitière Numérique", "Glacier Systèmes", "Lauze Bâtiment",
    "Moraine Mécanique", "Pierrier Robotique", "Sérac Conseil", "Torrent Automatismes",
    "Vallon Matériaux",
)  # fmt: skip

CITIES = (
    ("Annecy", "74000"), ("Chambéry", "73000"), ("Grenoble", "38000"), ("Lyon", "69003"),
    ("Genève", "1201"), ("Albertville", "73200"), ("Aix-les-Bains", "73100"), ("Thonon", "74200"),
)  # fmt: skip

INTERNSHIP_TITLES = (
    "Tableau de bord de production", "Jumeau numérique d'une ligne", "Capteurs sans fil",
    "Bilan carbone d'un site", "Refonte d'une application web", "Maintenance prédictive",
    "Isolation d'un bâtiment ancien", "Pilotage d'un robot", "Analyse de données qualité",
    "Simulation thermique",
)  # fmt: skip

FAKE_MAIL_DOMAIN = "example.org"
COMPONENT = "Polytech"


class InternshipNature(StrEnum):
    """Les natures de stage du jeu fictif."""

    ASSISTANT_ENGINEER = "assistant ingénieur"
    END_OF_STUDIES = "fin d'études"
