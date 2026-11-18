"""Fonctions d'introspection des clés primaires, secondaires et étrangères MySQL."""

import os
from typing import Any

import mysql.connector
import structlog
from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import PooledMySQLConnection

HOST = os.getenv("MYSQL_SERVER")
USER = os.getenv("MYSQL_USER_LOGIN")
PASSWORD = os.getenv("MYSQL_USER_PASSWORD")
DATABASE = os.getenv("MYSQL_DB")

logger = structlog.get_logger(__name__)

# A connection as mysql.connector.connect returns it.
type Connection = MySQLConnectionAbstract | PooledMySQLConnection


def request(query: str, param: tuple[Any, ...] = ()) -> list[Any]:
    conn = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
    )
    cursor = conn.cursor()
    try:
        cursor.execute(query, param)
        rows = cursor.fetchall()
    except mysql.connector.Error:
        logger.exception("init.query_failed")
        return []
    finally:
        cursor.close()

    res = [row[0] for row in rows]
    return res


def get_primary_key_fields(conn: Connection, table_name: str) -> list[Any]:
    """Retourne les colonnes de clé primaire d'une table."""
    mysql_db = os.getenv("MYSQL_DB")

    query = f"""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{mysql_db}'
          AND COLUMN_KEY = 'PRI'
          AND TABLE_NAME = '{table_name}'
    """

    cursor = conn.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
    except mysql.connector.Error:
        logger.exception("init.query_failed")
        return []
    finally:
        cursor.close()

    primary_keys = [row[0] for row in rows]
    return primary_keys


def get_secondary_key_fields(conn: Connection, table_name: str) -> list[Any]:
    """Retourne les colonnes de clé secondaire (index SECONDARY) d'une table."""
    query = (
        """
            SELECT column_name
            FROM information_schema.statistics
            WHERE table_schema =  '"""
        + os.getenv("MYSQL_DB")
        + """'
              AND table_name = '"""
        + table_name
        + """'
              AND INDEX_NAME = 'SECONDARY'
            """
    )

    cursor = conn.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
    except mysql.connector.Error:
        logger.exception("init.query_failed")
        return []
    finally:
        cursor.close()

    secondary_keys_fields = [row[0] for row in rows]
    return secondary_keys_fields


def get_foreign_keys(conn: Connection, table_name: str) -> dict[Any, Any]:
    """Retourne un dict {colonne_fk: table_référencée} pour une table."""
    query = (
        """
        SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME,
               REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE REFERENCED_TABLE_SCHEMA = '"""
        + os.getenv("MYSQL_DB")
        + """'
          AND TABLE_NAME = '"""
        + table_name
        + """'
    """
    )
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
    except mysql.connector.Error:
        logger.exception("init.query_failed")
        return {}
    finally:
        cursor.close()

    foreign_keys = {row[1]: row[3] for row in rows if row[3] is not None}
    return foreign_keys
