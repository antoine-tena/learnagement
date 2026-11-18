-- Une personne (login ou mail) n'est que dans une des tables LNM_administratif, LNM_enseignant,
-- LNM_etudiant : la connexion la cherche dans cet ordre et garderait la première trouvée.
-- Les doublons déjà présents restent ; db/tools/people_in_several_tables.sql les liste.

DELIMITER ;;

CREATE PROCEDURE assert_person_in_one_table(
    IN person_table VARCHAR(20),
    IN person_login VARCHAR(50),
    IN person_mail VARCHAR(50)
)
BEGIN
    IF (person_table <> 'administratif' AND EXISTS (
            SELECT 1 FROM LNM_administratif WHERE login = person_login OR mail = person_mail))
       OR (person_table <> 'enseignant' AND EXISTS (
            SELECT 1 FROM LNM_enseignant WHERE login = person_login OR mail = person_mail))
       OR (person_table <> 'etudiant' AND EXISTS (
            SELECT 1 FROM LNM_etudiant WHERE login = person_login OR mail = person_mail))
    THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'person already in another people table (login or mail)';
    END IF;
END;;

CREATE TRIGGER administratif_in_one_table_insert BEFORE INSERT ON LNM_administratif
FOR EACH ROW CALL assert_person_in_one_table('administratif', NEW.login, NEW.mail);;

CREATE TRIGGER administratif_in_one_table_update BEFORE UPDATE ON LNM_administratif
FOR EACH ROW
BEGIN
    IF NOT (NEW.login <=> OLD.login AND NEW.mail <=> OLD.mail) THEN
        CALL assert_person_in_one_table('administratif', NEW.login, NEW.mail);
    END IF;
END;;

CREATE TRIGGER enseignant_in_one_table_insert BEFORE INSERT ON LNM_enseignant
FOR EACH ROW CALL assert_person_in_one_table('enseignant', NEW.login, NEW.mail);;

CREATE TRIGGER enseignant_in_one_table_update BEFORE UPDATE ON LNM_enseignant
FOR EACH ROW
BEGIN
    IF NOT (NEW.login <=> OLD.login AND NEW.mail <=> OLD.mail) THEN
        CALL assert_person_in_one_table('enseignant', NEW.login, NEW.mail);
    END IF;
END;;

CREATE TRIGGER etudiant_in_one_table_insert BEFORE INSERT ON LNM_etudiant
FOR EACH ROW CALL assert_person_in_one_table('etudiant', NEW.login, NEW.mail);;

CREATE TRIGGER etudiant_in_one_table_update BEFORE UPDATE ON LNM_etudiant
FOR EACH ROW
BEGIN
    IF NOT (NEW.login <=> OLD.login AND NEW.mail <=> OLD.mail) THEN
        CALL assert_person_in_one_table('etudiant', NEW.login, NEW.mail);
    END IF;
END;;

DELIMITER ;
