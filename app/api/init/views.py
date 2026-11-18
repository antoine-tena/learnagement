"""Construction des vues ExplicitSecondaryKs_* et point d'entrée init()."""

from typing import Any

import mysql.connector
import structlog

from .introspection import (
    DATABASE,
    HOST,
    PASSWORD,
    USER,
    Connection,
    get_foreign_keys,
    get_primary_key_fields,
    get_secondary_key_fields,
    request,
)
from .queries import requests

logger = structlog.get_logger(__name__)


def __build_secondary_key_request(conn: Connection, table: str) -> dict[str, Any]:
    """Construit récursivement les clauses SELECT et FROM pour une vue ExplicitSecondaryKs."""
    primary_keys_fields = get_primary_key_fields(conn, table)
    foreign_keys_fields = get_foreign_keys(conn, table)
    secondary_keys_fields = get_secondary_key_fields(conn, table)

    request_as_dict: dict[str, Any] = {
        "SELECT": [],
        "SELECT_PRIM": [f"{table}.{pk}" for pk in primary_keys_fields],
        "FROM": "",
        "MAINTABLE": table,
    }

    for secondary_key_field in secondary_keys_fields:
        if secondary_key_field in foreign_keys_fields:
            sub_request = __build_secondary_key_request(
                conn, foreign_keys_fields[secondary_key_field]
            )

            request_as_dict["SELECT"].extend(sub_request["SELECT"])
            request_as_dict["SELECT_PRIM"].extend(sub_request["SELECT_PRIM"])

            sub_table = sub_request["MAINTABLE"]
            sub_primary = get_primary_key_fields(conn, foreign_keys_fields[secondary_key_field])[0]
            request_as_dict["FROM"] += (
                f" JOIN {sub_table} ON {sub_table}.{sub_primary} = {table}.{secondary_key_field}"
                f"{sub_request['FROM']}"
            )
        else:
            request_as_dict["SELECT"].append(f"{table}.{secondary_key_field}")

    return request_as_dict


def build_secondary_key_request(conn: Connection, table: str) -> str:
    primary_key_field = get_primary_key_fields(conn, table)[0]
    secondary_key_request_dict = __build_secondary_key_request(conn, table)

    select_fields = ", ".join(secondary_key_request_dict["SELECT"])
    select_prim_fields = ", ".join(secondary_key_request_dict["SELECT_PRIM"])
    from_clause = f"{table} {secondary_key_request_dict['FROM']}"

    secondary_key_request = f"""
        CREATE OR REPLACE VIEW ExplicitSecondaryKs_{table} AS
        SELECT {table}.{primary_key_field} AS id,
               CONCAT_WS(' ', {select_fields}) AS ExplicitSecondaryK,
               {select_prim_fields}
        FROM {from_clause}
    """

    return secondary_key_request


def init() -> None:
    conn = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
    )

    tables = request(requests["check"]["table_without_secondary_K"])
    for table in tables:
        logger.warning("init.table_without_secondary_key", table=table)

    tables = request(requests["check"]["primaryK_namming_error"])
    for table in tables:
        logger.warning("init.primary_key_misnamed", table=table)

    linked_tables = request(requests["struct"]["linked_table"])
    leaf_tables = request(requests["struct"]["leaf_table"])
    tables = linked_tables + leaf_tables

    for table in tables:
        query = build_secondary_key_request(conn, table)
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            cursor.fetchall()
        except mysql.connector.Error:
            logger.exception("init.secondary_key_view_failed", table=table)
        finally:
            cursor.close()

    conn.close()
    logger.info("init.done")
