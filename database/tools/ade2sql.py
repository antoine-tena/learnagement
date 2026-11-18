from ics import Calendar
import requests
import mysql.connector
import config
import datetime

reqEnseignants = "SELECT id_enseignant, nom, prenom FROM INFO_enseignant"
reqModules = "SELECT id_module, code FROM INFO_module"

insSeances = "INSERT IGNORE INTO INFO_seance (type, date, duree, id_module, id_enseignant) VALUES (%s, %s, %s, %s, %s)"
val=[]

enseignants = {}
modules={}
with mysql.connector.connect(**config.connection_params) as db :
    with db.cursor() as c:
        c.execute(reqEnseignants)
        resultats = c.fetchall()
        for enseignant in resultats:
            enseignants[enseignant[1].upper()+ " "+enseignant[2].upper()] = enseignant[0]

        c.execute(reqModules)
        resultats = c.fetchall()
        for module in resultats:
            modules[module[1]]=module[0]



# Parse the URL
for enseignant in enseignants.keys():
    if enseignant in  config.adeLinks:
        url = config.adeLinks[enseignant]
        cal = Calendar(requests.get(url).text)

        # Print all the events
        for event in cal.events:
            #print("begin: ", event._begin)
            #print("end: ", event._end_time)
            #print("name: ", event.name)
            #print("desc: ", event.description)
            #print()

            for module in modules.keys():
                if module in event.name:
                    date = event._begin.format('YYYY-MM-DD HH:mm')
                    duree =  event._end_time - event._begin #don't cast duree in str it is used later as timedelta
                    if "CM" in event.description:
                        #print("CM", date, duree, modules[module], enseignants[enseignant])
                        val = val + [("CM", date, str(duree), modules[module], enseignants[enseignant])]
                    elif "TD" in event.description and duree == datetime.timedelta(hours=4, minutes=0, seconds=0):
                        #print("TDP", date, duree, modules[module], enseignants[enseignant])
                        val = val + [("TDP", date, str(duree), modules[module], enseignants[enseignant])]
                    elif "TD" in event.description:
                        #print("TD", date, duree, modules[module], enseignants[enseignant])
                        val = val + [("TD", date, str(duree), modules[module], enseignants[enseignant])]
                    elif "TP" in event.description:
                        #print("TP", date, duree, modules[module], enseignants[enseignant])
                        val = val + [("TP", date, str(duree), modules[module], enseignants[enseignant])]
        print(val)
        with mysql.connector.connect(**config.connection_params) as db :
            with db.cursor() as c:
                c.executemany(insSeances, val)
                db.commit()
