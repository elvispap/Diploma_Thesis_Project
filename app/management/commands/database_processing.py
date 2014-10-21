import MySQLdb
import time
from django.db import IntegrityError
import urllib,urllib2
import json
import base64
import urlparse
import math
from functools import wraps
import uth_home_page 

connection = MySQLdb.connect(host="localhost",user="root",passwd="********",db="uth_research_db")
connection.set_character_set('utf8')
x = connection.cursor()

x.execute('SET GLOBAL connect_timeout=1000')
x.execute('SET NAMES utf8;') 
x.execute('SET CHARACTER SET utf8;')
x.execute('SET character_set_connection=utf8;')
x.execute('alter table `uth_research_db`.`app_affiliation` convert to character set utf8 collate utf8_general_ci;')
x.execute('alter table `uth_research_db`.`app_gen_affiliation` convert to character set utf8 collate utf8_general_ci;')
x.execute('alter table `uth_research_db`.`app_co_author` convert to character set utf8 collate utf8_general_ci;')
x.execute('alter table `uth_research_db`.`app_keyword` convert to character set utf8 collate utf8_general_ci;')
x.execute('alter table `uth_research_db`.`app_publication` convert to character set utf8 collate utf8_general_ci;')
x.execute('alter table `uth_research_db`.`app_publication_cited` convert to character set utf8 collate utf8_general_ci;')
x.execute('alter table `uth_research_db`.`app_subject_area` convert to character set utf8 collate utf8_general_ci;')


def start_processing(results,source,author):

    try:
        query = "SELECT * FROM app_author WHERE name = %s "
        x.execute(query,(author))
        row = x.fetchall()
        authorID = row[0][0]
        flag_1 = True       #for accessing the firt result from ieee only once
        flag_2 = True       #for accessing the firt result from scopus and microsoft only once
        
        author_last_name = author.split(" ")[1]
       
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
            pub_keywords = results[i]['keywords']
            pub_pubs_cited = results[i]['publications_cited']
            
            print "write to app_publication"
            x.execute("""INSERT INTO app_publication (pub_title,pub_url,pub_venue,pub_date,pub_type,pub_citations,pub_doi) VALUES (%s,%s,%s,%s,%s,%s,%s)""",[pub_title,pub_url,pub_venue,pub_date,pub_type,pub_citations,pub_doi])
            publicationID = x.lastrowid
            connection.commit()

            print "write to app_publication_author"
            x.execute("""INSERT INTO app_publication_author (publication_id,author_id) VALUES (%s,%s)""",[publicationID,int(authorID)])
            connection.commit()

            for keyword in pub_keywords:
                query = "SELECT * FROM app_keyword WHERE keyword LIKE %s"
                x.execute(query,["%" + keyword + "%"])
                connection.commit()
                row = x.fetchall()
                if  row:    # exists
                    keywordID =  row[0][0]
                    print "exists"
                
                else:   # not exists
                    print "write app_keyword"
                    x.execute("""INSERT INTO app_keyword (keyword,freq) VALUES (%s,%s)""",[keyword,0])
                    keywordID = x.lastrowid
                    connection.commit()
                 
                
                query = "SELECT * FROM app_keyword_publication WHERE publication_id = %s AND keyword_id = %s"
                x.execute(query,[publicationID,keywordID])
                row = x.fetchall()
                if not row:  # not exists
                    print "write app_keyword_publication"
                    x.execute("""INSERT INTO app_keyword_publication (keyword_id,publication_id) VALUES (%s,%s)""",[keywordID,publicationID])
                    connection.commit()

                    x.execute("""UPDATE app_keyword SET freq = freq + 1 WHERE id=%s""",[keywordID])
                    connection.commit()
                

            ###############################################################################################################
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
                    query = "SELECT * FROM app_publication_publication_cited WHERE publication_id = %s AND publication_cited_id = %s"
                    x.execute(query,[publicationID,pub_citedID])
                    row = x.fetchall()
                    if not row:
                        x.execute("""INSERT INTO app_publication_publication_cited (publication_id,publication_cited_id) VALUES (%s,%s)""",[publicationID,pub_citedID])
                        connection.commit()
            ###############################################################################################################    
            
            if source == "ieee":
                
                pub_authors = results[i]['authors']
                for author in pub_authors:
                    if author_last_name in author:
                        continue
                    
                    author_name_split = author.split(" ")
                    author_name_max_part = max(author_name_split, key=len)
                    
                    query = "SELECT * FROM app_co_author WHERE name LIKE %s "
                    x.execute(query,("%" + author_name_max_part + "%"))
                    connection.commit()
                    row = x.fetchall()
                    if  not row:   # not exists
                        print "write_co_author ieee"
                        x.execute("""INSERT INTO app_co_author (name,profile_url) VALUES (%s,%s)""",[author,"-"])
                        co_authorID = x.lastrowid
                        connection.commit()
                    else:
                        co_authorID = row[0][0]

                    query = "SELECT * FROM app_co_author_author WHERE co_author_id = %s AND author_id = %s "
                    x.execute(query,[int(co_authorID),int(authorID)])
                    connection.commit()
                    row = x.fetchall()
                    if  not row:   # not exists
                        print "write_co_author_author ieee"
                        x.execute("""INSERT INTO app_co_author_author (co_author_id,author_id) VALUES (%s,%s)""",[int(co_authorID),int(authorID)])
                        connection.commit()

                    query = "SELECT * FROM app_publication_co_author WHERE co_author_id = %s AND publication_id = %s "
                    x.execute(query,[int(co_authorID),int(publicationID)])
                    connection.commit()
                    row = x.fetchall()
                    if  not row:   # not exists
                        print "write_publication_co_author ieee"
                        x.execute("""INSERT INTO app_publication_co_author (co_author_id,publication_id) VALUES (%s,%s)""",[int(co_authorID),int(publicationID)])
                        connection.commit()

                if flag_1:
                    affiliations = results[0]['affiliations']
                    for affiliation in affiliations:
                        query = "SELECT * FROM app_gen_affiliation WHERE affiliation = %s"
                        x.execute(query,[affiliation])
                        connection.commit()
                        row = x.fetchall()
                        if  row: 
                            continue
                        else:  
                            x.execute("""INSERT INTO app_gen_affiliation (affiliation) VALUES (%s)""",[affiliation])
                            gen_affiliationID = x.lastrowid
                            connection.commit()
                            x.execute("""INSERT INTO app_gen_affiliation_author (gen_affiliation_id,author_id) VALUES (%s,%s)""",[int(gen_affiliationID),int(authorID)])
                            connection.commit()
                    flag_1 = False      
            else:   #scopus or microsoft
                authors_affiliations = results[i]['authors_affiliations']
                for author_affiliation in authors_affiliations:

                    author = author_affiliation[0]
                    if author_last_name in author:
                        continue

                    affiliation = author_affiliation[1] 
                    author_url = author_affiliation[2]
                    category = author_affiliation[3]
                    country = ""

                    if category == "external":
                        print "external"
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

                        author_name_split = author.split(" ")
                        author_name_max_part = max(author_name_split, key=len)
                        
                        query = "SELECT * FROM app_co_author WHERE name LIKE %s"
                        x.execute(query,["%" + author_name_max_part + "%"])
                        row = x.fetchall()
                        
                        if not row:  #not exists
                            print "write app_co_author"
                            x.execute("""INSERT INTO app_co_author (name,profile_url) VALUES (%s,%s)""",[author,author_url])     
                            connection.commit()
                            co_authorID = x.lastrowid
                        else:
                            co_authorID = row[0][0] 

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
                            
                            query = "SELECT * FROM app_co_author_affiliation WHERE co_author_id = %s"
                            x.execute(query,[int(co_authorID)])
                            row = x.fetchall()
                            if not row:  # not exists
                                x.execute("""INSERT INTO app_co_author_affiliation (affiliation_id,co_author_id) VALUES (%s,%s)""",[int(affiliationID),(int(co_authorID))])
                                connection.commit()
                        

                        query = "SELECT * FROM app_co_author_author WHERE co_author_id = %s AND author_id = %s"
                        x.execute(query,[int(co_authorID),int(authorID)])
                        row = x.fetchall()

                        if not row:  
                            print "write app_co_author_author"
                            x.execute("""INSERT INTO app_co_author_author (co_author_id,author_id) VALUES (%s,%s)""",[int(co_authorID),int(authorID)])
                            connection.commit()

                        query = "SELECT * FROM app_publication_co_author WHERE co_author_id = %s AND publication_id = %s "
                        x.execute(query,[int(co_authorID),int(publicationID)])
                        connection.commit()
                        row = x.fetchall()
                        if  not row:   # not exists
                            print "write app_publication_co_author"
                            x.execute("""INSERT INTO app_publication_co_author (co_author_id,publication_id) VALUES (%s,%s)""",[int(co_authorID),int(publicationID)])
                            connection.commit()   

                    else:   # department's author

                        authorID = author_affiliation[4]
                        #publicationID = author_affiliation[5]       # remove this
                        query = "SELECT * FROM app_publication_author WHERE author_id = %s AND publication_id = %s "
                        x.execute(query,[int(authorID),int(publicationID)])
                        connection.commit()
                        row = x.fetchall()
                        if  not row:   # not exists
                            print "write interior app_publication_author"
                            x.execute("""INSERT INTO app_publication_author (author_id,publication_id) VALUES (%s,%s)""",[int(authorID),int(publicationID)])
                            connection.commit()   

                if flag_2:
                   
                    subject_areas = results[0]['subject_areas']
                    for area in subject_areas:
                        query = "SELECT * FROM app_subject_area WHERE area LIKE %s"
                        x.execute(query,["%" + area.strip() + "%"])
                        connection.commit()
                        row = x.fetchall()
                        
                        if  row:   # exists
                            subject_areaID =  row[0][0]
                        else:       # doesn't exist
                            x.execute("""INSERT INTO app_subject_area (area) VALUES (%s)""",[area])
                            connection.commit()
                            subject_areaID =  x.lastrowid

                        query = "SELECT * FROM app_subject_area_author WHERE subject_area_id = %s AND author_id = %s"
                        x.execute(query,[int(subject_areaID),int(authorID)])
                        row = x.fetchall()
                        if not row:  
                            x.execute("""INSERT INTO app_subject_area_author (subject_area_id,author_id) VALUES (%s,%s)""",[int(subject_areaID),int(authorID)])
                            connection.commit()

                    flag_2 = False      
                
        
        
        query = "SELECT * FROM app_department_name"        # find the name of the department
        x.execute(query)
        row = x.fetchall()
        department = row[0][1]
        uth_home_page.write_to_central_database(results,source,department)       # write to central database      
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

def check_duplicates(seq1,seq2,seq3):

    a = seq1.lower()
    a_split = a.split(" ")
    a_list_max = max(a_split, key=len)

    b = seq3.lower()
    b_split = b.split(" ")
    b_list_max = max(b_split, key=len)

    if a_list_max in b_split:
        return True
    if b_list_max in a_split:
        return True    

    seq2_lower = [x.lower() for x in seq2]

    for element in seq2_lower:
        element_split = element.split(" ")
        element_max = max(element_split, key=len)
        if element_max in a_split or a_list_max in element:
            return True
    
    for element in seq2_lower:
        if difflib.SequenceMatcher(None, element, a).ratio() > 0.85:
            return True
    return False

 
