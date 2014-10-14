import MySQLdb
from crawlers import microsoft
from crawlers import ieee
from crawlers import scopus
from django.db import IntegrityError
import base64
import database_processing


connection = MySQLdb.connect(host="localhost",user="root",passwd="",db="uth_research_db")
connection.set_character_set('utf8')
x = connection.cursor()
x.execute('SET GLOBAL connect_timeout=1000')
x.execute('SET NAMES utf8;') 
x.execute('SET CHARACTER SET utf8;')
x.execute('SET character_set_connection=utf8;')


def start_crawling(author):

    # print "-----------------------FROM SCOPUS %s -----------------------" % author
    # authorID = find_authorID(author,"scopus")
   
    
    # if authorID == None or authorID == "":
    #     print "No results from Scopus"
    # else:
    #     results_from_scopus = scopus.start_crawling(author,authorID)
    #     if results_from_scopus == None:
    #         print "No results"
    #     else:
    #         database_processing.start_processing(results_from_scopus,"scopus",author)
    
    
   
    print "-----------------------FROM MICROSOFT %s -----------------------" % author
    authorID = find_authorID(author,"microsoft")
    
    if authorID == None or authorID == "":
        print "No results from microsoft"
    else:
        results_from_microsoft = microsoft.start_crawling(author,authorID)
        if results_from_microsoft == None:
            print "No results"
            
        else:
            print "write to db"
            database_processing.start_processing(results_from_microsoft,"microsoft",author)

    print "-----------------------FROM IEEE %s -----------------------" % author
    query = "SELECT * FROM app_author WHERE name = %s"
    x.execute(query,(author))
    row = x.fetchall()
    if row[0][6] != "":
        name_to_search = row[0][6]
    else:
        name_to_search = ""
    results_from_ieee = ieee.start_crawling(author,name_to_search)
    
    if results_from_ieee == None:
        print "No results"
        
    else:
        database_processing.start_processing(results_from_ieee,"ieee",author)

   
def find_authorID(author,source):
    try:
        query = "SELECT * FROM app_author where name = %s"
        x.execute(query,(author))
        row = x.fetchall()
        if row:
            if source == "microsoft":
                return row[0][5]
            else:
                return row[0][4]
        else:
            return None
    except AttributeError:
        return None
 