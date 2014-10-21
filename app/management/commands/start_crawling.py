import MySQLdb
import request_results
import time
from django.db import IntegrityError
import base64
import urlparse
from contextlib import closing
from functools import wraps
from django.core.management.base import NoArgsCommand, CommandError


class Command(NoArgsCommand):

    help = " Start the crawling process "

    def handle_noargs(self, **options):

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
        x.execute('alter table `uth_research_db`.`app_subject_area` convert to character set utf8 collate utf8_general_ci;')

        
        query = "SELECT * FROM app_author"
        x.execute(query)
        connection.commit()
        row = x.fetchall()
        
        for author in row:
            author_name = author[1]
            print author_name
            request_results.start_crawling(author_name)
            time.sleep(5)               #wait 5sec before crawling for the next author
        
        x.close()

    
   





        
    
    
