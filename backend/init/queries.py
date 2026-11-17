"""Requêtes d'introspection du schéma MySQL pour l'initialisation."""

import os

requests: dict[str, dict[str, str]] = {"check": {}, "struct": {}, "api": {}}

# Return table without secondary key, that's prohibited by the framework
requests["check"]["table_without_secondary_K"] = (
    """
    SELECT DISTINCT `TABLE_NAME`
    FROM `information_schema`.`KEY_COLUMN_USAGE`
    WHERE `TABLE_SCHEMA` =  '"""
    + os.getenv("MYSQL_DB")
    + """'
        and `TABLE_NAME` not in
            (SELECT `TABLE_NAME` AS `TABLE_NAME`
            FROM `information_schema`.`KEY_COLUMN_USAGE`
            WHERE `TABLE_SCHEMA` = '"""
    + os.getenv("MYSQL_DB")
    + """'
                AND `CONSTRAINT_NAME` = 'SECONDARY');"""
)

# Return table with error in their primary key name.
# According to the framework, the table XXXX_name has id_name as primary key.
requests["check"]["primaryK_namming_error"] = (
    """
    SELECT DISTINCT TABLE_NAME, COLUMN_NAME, TRIM( SUBSTR(TABLE_NAME, LOCATE('_', TABLE_NAME)) ),
        TRIM( SUBSTR(COLUMN_NAME, LOCATE('_', COLUMN_NAME)) )
    FROM `information_schema`.`KEY_COLUMN_USAGE`
    WHERE `TABLE_SCHEMA` =  '"""
    + os.getenv("MYSQL_DB")
    + """'
        AND `CONSTRAINT_NAME` LIKE "PRIMARY"
        AND TABLE_NAME IN
            (SELECT DISTINCT TABLE_NAME
            FROM `information_schema`.`KEY_COLUMN_USAGE`
            WHERE `TABLE_SCHEMA` =  '"""
    + os.getenv("MYSQL_DB")
    + """'
                AND `CONSTRAINT_NAME` LIKE "PRIMARY"
            GROUP BY TABLE_NAME
            HAVING COUNT(*)=1)
                AND TRIM( SUBSTR(TABLE_NAME, LOCATE('_',
                    TABLE_NAME)) ) != TRIM( SUBSTR(COLUMN_NAME, LOCATE('_', COLUMN_NAME)) );"""
)

# Return transition tables, according to the framework table that primary keys
# are composed by 2 attributes
requests["struct"]["link_table"] = (
    """
    SELECT `TABLE_NAME` AS `TABLE_NAME`
    FROM `information_schema`.`KEY_COLUMN_USAGE`
    WHERE `TABLE_SCHEMA` =  '"""
    + os.getenv("MYSQL_DB")
    + """'
        AND `CONSTRAINT_NAME` = 'PRIMARY'
    GROUP BY `TABLE_NAME`
    HAVING count(0) >= 2;"""
)

# Return linked table that are not transition tables
requests["struct"]["linked_table"] = (
    """
    SELECT DISTINCT `TABLE_NAME`
    FROM `information_schema`.`KEY_COLUMN_USAGE`
    WHERE `TABLE_SCHEMA` =  '"""
    + os.getenv("MYSQL_DB")
    + """'
        AND `CONSTRAINT_NAME` LIKE "FK%"
        AND `TABLE_NAME` NOT IN
            (SELECT `TABLE_NAME` AS `TABLE_NAME`
            FROM `information_schema`.`KEY_COLUMN_USAGE`
            WHERE `TABLE_SCHEMA` =  '"""
    + os.getenv("MYSQL_DB")
    + """'
                AND `CONSTRAINT_NAME` = 'PRIMARY'
            GROUP BY `TABLE_NAME`
            HAVING count(0) >= 2);"""
)

# Return leaf table: without foreign keys
requests["struct"]["leaf_table"] = (
    """
    SELECT DISTINCT `TABLE_NAME` AS `TABLE_NAME`
    FROM `information_schema`.`KEY_COLUMN_USAGE`
    WHERE `TABLE_SCHEMA` =  '"""
    + os.getenv("MYSQL_DB")
    + """'
    AND `TABLE_NAME` NOT IN
        (SELECT `TABLE_NAME`
        FROM `information_schema`.`KEY_COLUMN_USAGE`
        WHERE `TABLE_SCHEMA` = '"""
    + os.getenv("MYSQL_DB")
    + """'
            AND `CONSTRAINT_NAME` LIKE "FK%")"""
)

# Return links from TABLE_NAME to REFERENCED_TABLE_NAME
requests["struct"]["link"] = (
    """
    SELECT DISTINCT TABLE_NAME, REFERENCED_TABLE_NAME
    FROM `information_schema`.`KEY_COLUMN_USAGE`
    WHERE `TABLE_SCHEMA` =  '"""
    + os.getenv("MYSQL_DB")
    + """'
        AND `CONSTRAINT_NAME` LIKE "FK%";"""
)

requests["api"]["primary_key"] = (
    """
    SELECT COLUMN_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = '"""
    + os.getenv("MYSQL_DB")
    + """'
        AND COLUMN_KEY = 'PRI'
        AND TABLE_NAME = %s
"""
)

requests["api"]["secondary_key"] = """

"""
