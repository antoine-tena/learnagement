-- Les personnes présentes dans plusieurs tables (même login ou même mail), à régler à la main.
-- N'affiche que les identifiants internes : ni nom, ni mail, ni login.
SELECT 'administratif-enseignant' AS tables, a.id_administratif AS id_first, e.id_enseignant AS id_second
FROM LNM_administratif a
JOIN LNM_enseignant e ON e.login = a.login OR e.mail = a.mail
UNION ALL
SELECT 'administratif-etudiant', a.id_administratif, s.id_etudiant
FROM LNM_administratif a
JOIN LNM_etudiant s ON s.login = a.login OR s.mail = a.mail
UNION ALL
SELECT 'enseignant-etudiant', e.id_enseignant, s.id_etudiant
FROM LNM_enseignant e
JOIN LNM_etudiant s ON s.login = e.login OR s.mail = e.mail;
