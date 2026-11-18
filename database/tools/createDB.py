from ics import Calendar
import requests
import mysql.connector
import config

def executeScriptsFromFile(cursor, filename):
    fd = open(filename, 'r')
    sqlFile = fd.read()
    fd.close()
    sqlCommands = sqlFile.split(';')

    for command in sqlCommands:
        try:
            if command.strip() != '':
                cursor.execute(command)
        except IOError as e:
            print("Command skipped: ", e)

# SQL file to create the tables
sqlTableSkeleton = "database/migrations/table_skeleton.sql"

# SQL file to create the views
sqlViewSkeleton = "database/migrations/table_skeleton.sql"

# SQL free data file
# Be careful the order is important due to foreign keys
freeData=[
    "INFO_filiere.sql",
    "INFO_enseignant.sql",
    "INFO_etudiant.sql",
    "INFO_promo.sql",
    "INFO_module.sql",
    "INFO_module_as_promo.sql"
          ]

with mysql.connector.connect(**config.connection_params) as db :
    with db.cursor() as c:
        executeScriptsFromFile(c, sqlTableSkeleton)
        executeScriptsFromFile(c, sqlViewSkeleton)
        for sqlFile in freeData:
            executeScriptsFromFile(c, sqlFile)
