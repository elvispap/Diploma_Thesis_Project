import MySQLdb
import time
from django.db import IntegrityError
import urllib,urllib2
import json
import base64
import urlparse
import math
from functools import wraps

connection = MySQLdb.connect(host="localhost",user="root",passwd="",db="uth_research_central_db")
connection.set_character_set('utf8')
x = connection.cursor()

x.execute('SET GLOBAL connect_timeout=1000')
x.execute('SET NAMES utf8;') 
x.execute('SET CHARACTER SET utf8;')
x.execute('SET character_set_connection=utf8;')
x.execute('alter table `uth_research_central_db`.`app_affiliation` convert to character set utf8 collate utf8_general_ci;')
x.execute('alter table `uth_research_central_db`.`app_publication` convert to character set utf8 collate utf8_general_ci;')
x.execute('alter table `uth_research_central_db`.`app_publication_cited` convert to character set utf8 collate utf8_general_ci;')
x.execute('alter table `uth_research_central_db`.`app_subject_area` convert to character set utf8 collate utf8_general_ci;')


def write_to_central_database(results,source,department_name): 
    try:
        
        flag_1 = True       #for accessing the firt result from ieee only once
        flag_2 = True       #for accessing the firt result from scopus and microsoft only once

        query = "SELECT name FROM app_departments WHERE name LIKE %s "
        x.execute(query,["%" + str(department_name) + "%"])
        row = x.fetchall()
        department_id = row[0][0]

        for i in range(1,len(results)):       
            
            pub_title = results[i]['title']
            if pub_title == "-":
                continue
            
            pub_doi = results[i]['doi']
            pub_url = results[i]['url']
            pub_venue = results[i]['venue']
            pub_date = results[i]['date']
            pub_type = results[i]['type']
            pub_citations = results[i]['citations']
            pub_pubs_cited = results[i]['publications_cited']
            
            x.execute("""INSERT INTO app_publication (pub_title,pub_url,pub_venue,pub_date,pub_type,pub_citations,pub_doi,department) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",[pub_title,pub_url,pub_venue,pub_date,pub_type,pub_citations,pub_doi,department_name])
            publicationID = x.lastrowid
            connection.commit()

            query = "SELECT * FROM app_publication_department WHERE publication_id = %s AND department_id = %s"
            x.execute(query,[int(publicationID),int(department_id)])
            row = x.fetchall()
            if not row:     # not exists
                x.execute("""INSERT INTO app_publication_department (publication_id,department_id) VALUES (%s,%s)""",[int(publicationID),(int(department_id))])
                connection.commit()   

            if pub_pubs_cited:
                for pub in pub_pubs_cited:

                    pub_cited_title = pub[0]
                    pub_cited_url = pub[1]
                    
                    query = "SELECT * FROM app_publication_cited WHERE pub_title LIKE %s"
                    x.execute(query,["%" + pub_cited_title +"%"])
                    row = x.fetchall()
                    if  row:   # exists
                        pub_citedID = row[0][0]
                       
                    else:       # not exists
                        x.execute("""INSERT INTO app_publication_cited (pub_title,pub_url) VALUES (%s,%s)""",[pub_cited_title,pub_cited_url])
                        pub_citedID = x.lastrowid
                        connection.commit()

                    query = "SELECT * FROM app_publication_cited_department WHERE publication_cited_id = %s AND department_id = %s"
                    x.execute(query,[int(pub_citedID),int(department_id)])
                    row = x.fetchall()
                    if not row:     # not exists
                        x.execute("""INSERT INTO app_publication_cited_department (publication_cited_id,department_id) VALUES (%s,%s)""",[int(pub_citedID),(int(department_id))])
                        connection.commit()   
             
            if source == "ieee":
              
                if flag_1:
                    affiliations = results[0]['affiliations']
                    for affiliation in affiliations:

                        country = ""
                        aff_location = ""
                        if affiliation != "":
                            address = affiliation.replace("\n", "")
                            result =  geocoding(address) 
                            if result != "":
                                data = json.load(result)

                                if data["status"][0] != "Z":
                                    # find the location of the affiliation
                                    for res in data['results']:
                                        lat = res['geometry']['location']['lat']
                                        lng = res['geometry']['location']['lng']
                                        aff_location = str(lat)+","+str(lng)

                                        # find the country of the affiliation
                                        for address_component in res['address_components']:
                                            if address_component['types'] == ['country', 'political']:
                                                country = address_component['long_name']
                                        break
                            else:
                                aff_location = ""

                            if affiliation != "":
                                new_affiliation = affiliation
                            if "university" in affiliation:
                                new_affiliation = affiliation.replace("university","")
                            
                            query = "SELECT * FROM `app_affiliation` WHERE affiliation_name = %s"
                            x.execute(query,[new_affiliation])
                            row1 = x.fetchall()
                            if  not row1:   # not exists
                               
                                x.execute("""INSERT INTO app_affiliation (affiliation_name,affiliation_location,affiliation_country) VALUES (%s,%s,%s)""",[affiliation,aff_location,country])
                                affiliationID = x.lastrowid
                                connection.commit()
                            else:
                                affiliationID = row1[0][0]
                            
                            query = "SELECT * FROM app_affiliation_department WHERE affiliation_id = %s AND department_id = %s"
                            x.execute(query,[int(affiliationID),int(department_id)])
                            row = x.fetchall()
                            if not row:  # not exists
                                x.execute("""INSERT INTO app_affiliation_department (affiliation_id,department_id) VALUES (%s,%s)""",[int(affiliationID),(int(department_id))])
                                connection.commit()   
                        
                    flag_1 = False      
            else:   #scopus or microsoft
                authors_affiliations = results[i]['authors_affiliations']
                for author_affiliation in authors_affiliations:

                    affiliation = author_affiliation[1] 
                    author_url = author_affiliation[2]
                    category = author_affiliation[3]
                    country = ""
                    aff_location = ""
                    if affiliation != "":
                        address = affiliation.replace("\n", "")
                        result =  geocoding(address) 
                        if result != "":
                            data = json.load(result)

                            if data["status"][0] != "Z":
                                # find the location of the affiliation
                                for res in data['results']:
                                    lat = res['geometry']['location']['lat']
                                    lng = res['geometry']['location']['lng']
                                    aff_location = str(lat)+","+str(lng)

                                    # find the country of the affiliation
                                    for address_component in res['address_components']:
                                        if address_component['types'] == ['country', 'political']:
                                            country = address_component['long_name']
                                    break
                            else:
                                aff_location = ""
                        else:
                            aff_location = ""

                        if affiliation != "":
                            new_affiliation = affiliation
                            if "university" in affiliation:
                                new_affiliation = affiliation.replace("university","")
                            
                            query = "SELECT * FROM `app_affiliation` WHERE affiliation_name = %s"
                            x.execute(query,[new_affiliation])
                            row1 = x.fetchall()
                            if  not row1:   # not exists
                                print "write affiliation"
                                x.execute("""INSERT INTO app_affiliation (affiliation_name,affiliation_location,affiliation_country) VALUES (%s,%s,%s)""",[affiliation,aff_location,country])
                                affiliationID = x.lastrowid
                                connection.commit()
                            else:
                                affiliationID = row1[0][0]
                            
                            query = "SELECT * FROM app_affiliation_department WHERE affiliation_id = %s AND department_id = %s"
                            x.execute(query,[int(affiliationID),int(department_id)])
                            row = x.fetchall()
                            if not row:  # not exists
                                x.execute("""INSERT INTO app_affiliation_department (affiliation_id,department_id) VALUES (%s,%s)""",[int(affiliationID),(int(department_id))])
                                connection.commit()
                       
                if flag_2:
                   
                    subject_areas = results[0]['subject_areas']
                    for area in subject_areas:
                        query = "SELECT * FROM app_subject_area WHERE area LIKE %s"
                        x.execute(query,["%" + area.strip() + "%"])
                        row = x.fetchall()
                        if  not row:   # exists
                            x.execute("""INSERT INTO app_subject_area (area) VALUES (%s)""",[area])
                            areanID = x.lastrowid
                            connection.commit()
                        else:
                            areanID = row[0][0]

                        query = "SELECT * FROM app_subject_area_department WHERE subject_area_id = %s AND department_id = %s"
                        x.execute(query,[int(areanID),int(department_id)])
                        row = x.fetchall()
                        if not row:  # not exists
                            x.execute("""INSERT INTO app_subject_area_department (subject_area_id,department_id) VALUES (%s,%s)""",[int(areanID),(int(department_id))])
                            connection.commit()
                    flag_2 = False      
                
    except IntegrityError:
        print "duplicate entry"
        return "END"


def geocoding(affiliation):  
   
    try:
        quoted_query = urllib.quote(affiliation)
        url = "http://maps.googleapis.com/maps/api/geocode/json?address=%s" % quoted_query

        response = urllib2.Request(url)
        response.add_headers = [('User-agent', 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36')]
        jsongeocode = urllib2.urlopen(response)
        
        return jsongeocode
    except KeyError:
        return ""
    