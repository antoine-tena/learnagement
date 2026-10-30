"""Les extractions, sur de petites pages fictives : aucun réseau."""

from learnagement_scraping import parsers


def test_select_options_ignores_placeholder_and_blanks() -> None:
    html = """
    <select id="discipline">
      <option>---</option><option> Info </option><option></option><option>Maths</option>
    </select>
    """
    assert parsers.select_options(html, "discipline") == ["Info", "Maths"]


def test_next_page_removes_the_site_domain() -> None:
    html = f'<a href="{parsers.SITE_URL}/liste?nextPage=2">Suivant</a>'
    assert parsers.next_page(html) == "/liste?nextPage=2"


def test_next_page_is_none_on_the_last_page() -> None:
    assert parsers.next_page('<a href="/liste?page=1">Précédent</a>') is None


def test_link_by_title() -> None:
    html = '<a title="Accéder aux programmes" href="/programmes">Programmes</a>'
    assert parsers.link_by_title(html, "Accéder aux programmes") == "/programmes"
    assert parsers.link_by_title(html, "Autre") is None


def test_teachers_reads_each_card_and_skips_incomplete_ones() -> None:
    html = """
    <div class="info">
      <p class="name">DUPONT Alice</p><p class="email">Mail : alice@example.org</p>
    </div>
    <div class="info"><p class="name">SANSMAIL Bob</p></div>
    """
    assert parsers.teachers(html) == [
        parsers.Teacher(nom="DUPONT", prenom="Alice", mail="alice@example.org")
    ]


def test_students_splits_status_and_name() -> None:
    html = """
    <div class="etudiant">
      <p class="statut"> FI4 - EIT</p><p class="name">MARTIN Chloé</p>
    </div>
    <div class="etudiant"><p class="statut">incomplet</p><p class="name">X Y</p></div>
    """
    assert parsers.students(html) == [
        parsers.Student(annee="FI4", filiere="EIT", nom="MARTIN", prenom="Chloé")
    ]


def test_module_links_keep_only_long_links_with_their_code() -> None:
    long_path = "/m?" + "x" * parsers.MODULE_LINK_MIN_LENGTH
    html = f"""
    <a href="/court">Accueil</a>
    <ul><li class="code">Code : INFO731</li></ul>
    <a href="{long_path}">Réseaux</a>
    """
    assert parsers.module_links(html) == [
        parsers.ModuleLink(code="INFO731", nom="Réseaux", url=f"{parsers.SITE_URL}{long_path}")
    ]


def test_module_details_pairs_labels_and_values() -> None:
    html = """
    <div class="label">Nb heures TD</div><div class="value"> 12 </div>
    <div class="label">Nb heures TP</div><div class="value"></div>
    """
    assert parsers.module_details(html) == {"Nb heures TD": "12"}


def test_profile_reads_the_table() -> None:
    html = """
    <table class="table table-bordered table-condensed">
      <tr><th>Prénom</th><td>Chloé</td></tr>
      <tr><th>Nom usuel</th><td>MARTIN</td></tr>
      <tr><th>Date de naissance</th><td> 01/01/2000 </td></tr>
    </table>
    """
    assert parsers.profile(html) == parsers.Profile("MARTIN", "Chloé", "01/01/2000")


def test_profile_is_none_when_a_field_is_missing() -> None:
    html = '<table class="table table-bordered table-condensed"><tr><th>Prénom</th><td>C</td></tr>'
    assert parsers.profile(html) is None
    assert parsers.profile("<p>Connexion refusée</p>") is None


def test_grades_groups_subjects_under_their_unit() -> None:
    html = """
    <table id="tableau">
      <tr><th>En-tête</th></tr>
      <tr><td><b>UE 1</b></td><td>14</td><td>20</td></tr>
      <tr><td>Réseaux</td><td>15</td><td>20</td></tr>
      <tr><td><b>UE 2</b></td><td>9</td><td>20</td></tr>
      <tr><td>Moyenne générale</td></tr>
    </table>
    """
    assert parsers.grades(html) == [
        {
            "Epreuve": "UE 1",
            "Note_dividende": "14",
            "Note_diviseur": "20",
            "Matières": [{"Epreuve": "Réseaux", "Note_dividende": "15", "Note_diviseur": "20"}],
        },
        {"Epreuve": "UE 2", "Note_dividende": "9", "Note_diviseur": "20", "Matières": []},
    ]


def test_grades_without_table_is_empty() -> None:
    assert parsers.grades("<p>Non connecté</p>") == []


def test_polypoints_ignores_other_blocks() -> None:
    html = """
    <div class="value"><ul>
      <li class="intitule">BDE</li><li class="intitule_tache">Accueil</li>
      <li class="nb_points">3</li><li class="annee">2025-2026</li>
    </ul></div>
    <div class="value">Autre chose</div>
    """
    assert parsers.polypoints(html) == [parsers.Polypoint("BDE", "Accueil", "3", "2025-2026")]


def test_internships_converts_dates_to_iso() -> None:
    html = """
    <div class="value"><ul>
      <li class="entreprise">Exemple SA - Annecy</li>
      <li class="date">du 01/06/2026 au 31/08/2026</li>
    </ul></div>
    <div class="value"><ul>
      <li class="entreprise">Sans date - Lyon</li><li class="date">à venir</li>
    </ul></div>
    """
    assert parsers.internships(html) == [
        parsers.Internship("Exemple SA", "Annecy", "2026-06-01", "2026-08-31")
    ]
