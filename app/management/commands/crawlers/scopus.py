import MySQLdb
import socket
import requests
import urllib2, base64
import urllib
from urllib2 import Request, urlopen, URLError, HTTPError
import urlparse
from bs4 import BeautifulSoup
import re
import time
from contextlib import closing
import math
from functools import wraps
import httplib


execeptions = (socket.error,urllib2.HTTPError,urllib2.URLError,httplib.HTTPException)
execeptions1 = (socket.error,urllib2.URLError,httplib.HTTPException)

#############################################################################################################################
connection = MySQLdb.connect(host="localhost",user="root",passwd="********",db="uth_research_db")
connection.set_character_set('utf8')
cur = connection.cursor()
cur.execute('SET NAMES utf8;') 
cur.execute('SET CHARACTER SET utf8;')
cur.execute('SET character_set_connection=utf8;')
cur.execute('alter table `uth_research_db`.`app_affiliation` convert to character set utf8 collate utf8_general_ci;')
cur.execute('alter table `uth_research_db`.`app_gen_affiliation` convert to character set utf8 collate utf8_general_ci;')
cur.execute('alter table `uth_research_db`.`app_co_author` convert to character set utf8 collate utf8_general_ci;')
cur.execute('alter table `uth_research_db`.`app_keyword` convert to character set utf8 collate utf8_general_ci;')
cur.execute('alter table `uth_research_db`.`app_publication` convert to character set utf8 collate utf8_general_ci;')
cur.execute('alter table `uth_research_db`.`app_publication_cited` convert to character set utf8 collate utf8_general_ci;')
cur.execute('alter table `uth_research_db`.`app_subject_area` convert to character set utf8 collate utf8_general_ci;')
#############################################################################################################################



def retry(ExceptionToCheck, tries=4, delay=10, backoff=3, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck, e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print msg
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry

def remove_special_characters(string):

    all_chars = ['-','(',')','/','*',':','<','>','.',',']
    for char in all_chars:
        string = string.replace(char,' ')

    return string

@retry(execeptions, tries=4, delay=10, backoff=3)
def find_publication_title(soup):

    try:
        title = soup.find("span",class_="docTitle").find("a").text.strip()        # the title of publication
        if "&searchTerm=AU-ID%" in title:
            new_title = title.split("&searchTerm=AU-ID%")[0]
            return ' '.join(remove_special_characters(new_title.capitalize()).split())
        return ' '.join(remove_special_characters(title.capitalize()).split())
        
    except AttributeError:
        return "-"       #no title found

@retry(execeptions, tries=4, delay=10, backoff=3)
def find_publication_venue(soup):
    
    try:
        venue1 = soup.find("div",class_="paddingT5").find("h2",class_="sourceTitle").text.strip()
        return venue1
    except AttributeError:
        return "-"
   
@retry(execeptions, tries=4, delay=10, backoff=3)
def find_publication_date(soup):
    
    try:
        date = soup.find("div",class_="dataCol4").find("span").text.strip()
        if date == "" or date == 0:
            date = "-"
        return date
    except AttributeError:
        return "-"
   
@retry(execeptions, tries=4, delay=10, backoff=3)
def find_publication_type(soup):
    
    try:
        pub_type  = soup.find("div",class_="formatSourceExtended").find("strong",text = re.compile("Source Type")).next_sibling.strip().split(" ")[0]
        if pub_type == "Trade":
            return "Journal"
        else:
            return pub_type
    except AttributeError:
        return "-"


@retry(execeptions, tries=4, delay=10, backoff=3)
def find_publications_cited(soup,scopus_machineID):
    
    try:
        publications = []
        number_of_results = 20
        url_0 = soup.find("div",class_="dataCol6").find("a")["href"]
      
        url_1 = url_0.split("?eid=")
        cit_code = url_1[1].split("&")
        offset = 1
        
        new_url = "http://www.scopus.com/results/results.url?sort=plf-f&cite={0}&src=s&nlo=&nlr=&nls=&imp=t&sid={1}&sot=cite&sdt=a&sl=0&cl=t&offset={2}&origin=resultslist&ss=plf-f&ws=r-f&ps=r-f&cs=r-f&cc=10&txGid={3}". format (cit_code[0],scopus_machineID,offset,scopus_machineID)
        new_soup = get_soup(new_url)
     
        total_publications = new_soup.find("div",class_="resultsCountLabel").find("span",class_="resultsCount").text
        if total_publications < number_of_results:
            pages = 1
        else:
            pages = int(math.ceil(float(total_publications)/number_of_results))

        for each_page in range(0,pages): 

            all_pubs = new_soup.find("ul",id="documentListUl").findAll("li")
            for pub in all_pubs:
                
                pub_title = remove_special_characters(pub.find("span",class_="docTitle").find("a").text.strip().capitalize())
                
                pub_url = pub.find("span",class_="docTitle").find("a")["href"]
                publications.append((pub_title,pub_url))
               
            offset = offset + 20
            new_url = "http://www.scopus.com/results/results.url?sort=plf-f&cite={0}&src=s&nlo=&nlr=&nls=&imp=t&sid={1}&sot=cite&sdt=a&sl=0&cl=t&offset={2}&origin=resultslist&ss=plf-f&ws=r-f&ps=r-f&cs=r-f&cc=10&txGid={3}". format (cit_code[0],scopus_machineID,offset,scopus_machineID)
            new_soup = get_soup(new_url)
        return publications
        
    except TypeError:
        print "type error"
        return publications
    except ValueError:
        print "type error"
        return publications
    except AttributeError:
        print "no cited"
        return publications

@retry(execeptions, tries=4, delay=10, backoff=3) 
def find_publication_citations(soup):
    
    try:
        citations = soup.find("div",class_="citedHeader").find("h2").text.strip().split(" ")[2]
        return citations
    except AttributeError:
        return 0
   
@retry(execeptions, tries=4, delay=10, backoff=3) 
def find_publication_keywords(soup):

    try:
        keywords = []
        has_author_keywords = soup.find("h2",text=re.compile('Author keywords'))
        if has_author_keywords != None:
            author_keywords = has_author_keywords.find_next("p").text.strip().split(";")
            for keyword in author_keywords:
                keywords.append(' '.join(remove_special_characters(keyword.lower().strip()).split()))    

        has_indexed_keywords = soup.find("h2",text=re.compile('Indexed keywords')) 
        
        if has_indexed_keywords != None:
            index_keywords = has_indexed_keywords.find_next("p").text.strip()
            
            if "Engineering controlled terms:" in index_keywords:
                keywords_to_ret = index_keywords.split(":")[1].split(";")
                
                for keyword in keywords_to_ret:
                    keywords.append(' '.join(remove_special_characters(keyword.lower().strip()).split()))    
            elif "EMTREE drug terms:" in index_keywords:
                keywords_to_ret = index_keywords.split(":")[1].split(";")
                
                for keyword in keywords_to_ret:
                    keywords.append(' '.join(remove_special_characters(keyword.lower().strip()).split()))
            elif "EMTREE medical terms:" in index_keywords:
                keywords_to_ret = index_keywords.split(":")[1].split(";")
                
                for keyword in keywords_to_ret:
                    keywords.append(' '.join(remove_special_characters(keyword.lower().strip()).split()))
            else:
                keywords_to_ret = index_keywords.split(";")
                for keyword in keywords_to_ret:
                    keywords.append(' '.join(remove_special_characters(keyword.lower().strip()).split()))
        
        return keywords


    except socket.error:
        print "there was an error with the connection2"
        return keywords 
    except AttributeError:
        print "error"
        return keywords       #no keywords found

@retry(execeptions, tries=4, delay=10, backoff=3) 
def find_authors_and_affiliations(soup,author_name,all_department_authors):

    authors_affiliations = []
    author_last_name = author_name.split()[1]
    all_authors = soup.find("div",class_="dataCol3").find("span").findAll("a")
    for author in all_authors:
        if author_last_name in author.text:
            continue

        author_name = remove_special_characters(author.text.strip())

        result = is_department_author(author_name,all_department_authors)    # check if the author is from the department
        
        if result:
            authors_affiliations.append((author_name,"","","department",result)) 
        else:
            author_url = author["href"]
            author_affiliation = find_affiliation(author_url)
            if author_affiliation == None:
                authors_affiliations.append((author_name,"",author_url,"external"))
            else:
                authors_affiliations.append((author_name,author_affiliation,author_url,"external"))
           
        time.sleep(10)
    return authors_affiliations

def is_department_author(author_name,all_department_authors):

    author_name_split = author_name.split(" ")
    author_name_list_max = max(author_name_split, key=len)
    for each_author in all_department_authors:
        if author_name_list_max in each_author[1]:
            author_id = each_author[0]
            return author_id
    return False      

@retry(execeptions, tries=4, delay=10, backoff=3)    
def find_affiliation(url):
    try:
        soup = get_soup(url)
        affiliation = soup.find("div",class_="authAffilcityCounty").text.strip()
        return affiliation
    except AttributeError:
        return None      


@retry(execeptions, tries=4, delay=10, backoff=3)
def get_soup(url):

    try :
        username = "papa"
        password = "%pa14756"
        p = urllib2.HTTPPasswordMgrWithDefaultRealm()

        p.add_password(None, url, username, password)

        handler = urllib2.HTTPBasicAuthHandler(p)
        opener = urllib2.build_opener(handler)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36')]
        #opener.addheaders.append(('Cookie', 'scopus.machineID=C3B80D50103E7601258DEBCACC579EBB.mw4ft95QGjz1tIFG9A1uw'))
        urllib2.install_opener(opener)

        htmltext = opener.open(url).read()
        soup = BeautifulSoup(htmltext)
        return soup
    
    
    except AttributeError:
        return None
   

@retry(execeptions1, tries=4, delay=10, backoff=3)  
def get_author_soup(authorID,scopus_machineID,offset,sl):

    author_url = "http://www.scopus.com/results/results.url?sort=plf-f&src=s&nlo=&nlr=&nls=&sid={0}%3a470&sot=aut&sdt=a&sl={1}&s=AU-ID%28{2}%29&cl=t&offset={3}&origin=resultslist&ss=plf-f&ws=r-f&ps=r-f&cs=r-f&cc=10&txGid={4}". format (scopus_machineID,sl,authorID,offset,scopus_machineID)
    print author_url
    try :
        username = "papa"
        password = "%pa14756"
        p = urllib2.HTTPPasswordMgrWithDefaultRealm()

        p.add_password(None, author_url, username, password)

        handler = urllib2.HTTPBasicAuthHandler(p)
        opener = urllib2.build_opener(handler)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36')]
        #opener.addheaders.append(('Cookie', 'scopus.machineID=C3B80D50103E7601258DEBCACC579EBB.mw4ft95QGjz1tIFG9A1uw'))
        urllib2.install_opener(opener)
        
        htmltext = opener.open(author_url).read()
        
        soup = BeautifulSoup(htmltext)
        return [soup,sl]
            
    
    except AttributeError:
        return None
    except HTTPError:
        print "HTTP ERROR 404"
        sl = 18                # !!!!!!!!!!!!!!!!!
        author_url = "http://www.scopus.com/results/results.url?sort=plf-f&src=s&nlo=&nlr=&nls=&sid={0}%3a470&sot=aut&sdt=a&sl={1}&s=AU-ID%28{2}%29&cl=t&offset={3}&origin=resultslist&ss=plf-f&ws=r-f&ps=r-f&cs=r-f&cc=10&txGid={4}". format (scopus_machineID,sl,authorID,offset,scopus_machineID)
        htmltext = opener.open(author_url).read()
        soup = BeautifulSoup(htmltext)
        return [soup,sl]

@retry(execeptions, tries=4, delay=10, backoff=3)
def find_subject_areas(url):
    print "here"
    sub_areas = []
    try:
        soup = get_soup(url)
        all_areas = soup.find("div",id="authSecondList").findAll("div",class_="row6")[1].text.replace("\r","").replace("View More","").replace(u'\xa0', u' ').strip()
        all_areas1 = all_areas.split(",")
        for area in all_areas1:
            sub_areas.append(remove_special_characters(area.strip()).strip())
        return sub_areas
    except AttributeError:
        return sub_areas

@retry(execeptions, tries=4, delay=10, backoff=3)
def find_publication_doi(title):
    """ Find the digital object identifier (doi) from http://search.crossref.org of the publication """
    try:
        opener = urllib2.build_opener()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36')]
        urllib2.install_opener(opener)

        new_title = title.replace(" ","+")

        url = "http://search.crossref.org/?q=%s&page=1&rows=1" % new_title.encode('ascii', 'ignore')
        htmltext = opener.open(url).read()
        soup = BeautifulSoup(htmltext)

        doi = soup.find("div",class_="item-links").find("a")["href"]
        if "org/" not in doi:
            doi = soup.find("div",class_="item-links").findAll("a")
           
            new_doi = doi[1]["href"].split("org/")
            print new_doi[1]
            return new_doi[1]
        else:
            print doi.split("org/")[1]
            return doi.split("org/")[1]

    except AttributeError:
        print "no doi"
        return ""

@retry(execeptions, tries=4, delay=10, backoff=3)
def check_database(title,citations,author_name,url):
    """ Check the database if the current publication exists. If not, we check if its citations have changed and if yes,udpate the DB """
    
    try:
        query = "SELECT * FROM app_publication WHERE pub_title LIKE %s"
        cur.execute(query,["%" + title +"%"])
        connection.commit()
        row = cur.fetchall()
        if  row:    # exists
            if int(citations) > int(row[0][6]):      # the citations of this publication have changed     
                cur.execute("""UPDATE app_publication SET pub_citations=%s,pub_url=%s WHERE pub_title=%s""",[citations,url,title])
                connection.commit()
                
                # update also the entry in central database
                connection_2 = MySQLdb.connect(host="localhost",user="root",passwd="",db="uth_research_central_db")
                connection_2.set_character_set('utf8')
                x = connection_2.cursor()
                x.execute("""UPDATE app_publication SET pub_citations=%s WHERE pub_title=%s""",[citations,title])
                connection_2.commit()

            # check if this publication is related with  
            pub_id = row[0][0]  
            query = "SELECT (id) FROM app_author WHERE name=%s"
            cur.execute(query,[author_name])
            row = cur.fetchall()
            author_id = row[0][0]

            query = "SELECT * FROM app_publication_author WHERE publication_id = %s AND author_id = %s"
            cur.execute(query,[int(pub_id),int(author_id)])
            row = cur.fetchall()
            if not row:
                print "write to app_publication_author"
                cur.execute("""INSERT INTO app_publication_author (publication_id,author_id) VALUES (%s,%s)""",[int(pub_id),int(author_id)])
                connection.commit()

            return True          # there is a publication with this title,so ingore this publication
        else:
            return False        # there is not a publication with this title
    except AttributeError:
        print "AttributeError check db"
        return True

@retry(execeptions, tries=4, delay=10, backoff=3)   
def start_crawling(author,authorID):
    
    try:  
        publications = []       # a dictionary for saving all publication of the author 
        publication = {}
        number_of_results = 20
        
        if authorID == None or authorID == "":
            return None
        
        ####### find all the authors of the department #######
        all_department_authors = []
        query = "SELECT * FROM app_author"
        cur.execute(query)
        row = cur.fetchall()
        for a in row:
            author_entry = (a[0],a[1])        # id + name
            all_department_authors.append(author_entry)
        ######################################################

        titles = []                 
        urls = []
        c = 0
        c1 = 0
        author_name = author.split()
        offset = 1    # next offset -> 201
        
        author_url = "http://www.scopus.com/authid/detail.url?authorId=%s" % authorID
        #s = requests.session()
        results = requests.get(author_url)
        headers = results.headers
        scopus_machineID = headers["set-cookie"].split(";")[0].split("=")[1]
        sl = 17
        
        soup = get_author_soup(authorID,scopus_machineID,offset,sl)  
        if soup[0] == None :
            return None
       
        total_publications = soup[0].find("div",class_="resultsCountLabel")#.find("span",class_="resultsCount").text
        if total_publications == None:     # 1 result found

            print "1 result found"
            sl = soup[1]
            publication_title = remove_special_characters(soup[0].find("h1",class_="svTitle").text.strip().capitalize())
            publication_citations = find_publication_citations(soup[0])

            duplicate_publication = check_database(publication_title,publication_citations,author,[])
            if duplicate_publication == True:
                print "ALREADY EXISTS"
                return publications   
            print "NOT EXISTS scopus"

            publication['subject_areas'] = "-"
            publications.append(publication)
            publication = {}

            publication['title'] = publication_title
            publication['doi'] = find_publication_doi(publication_title)
            publication['url'] = "http://www.scopus.com/results/results.url?sort=plf-f&src=s&nlo=&nlr=&nls=&sid={0}%3a470&sot=aut&sdt=a&sl={1}&s=AU-ID%28{2}%29&cl=t&offset={3}&origin=resultslist&ss=plf-f&ws=r-f&ps=r-f&cs=r-f&cc=10&txGid={4}". format (scopus_machineID,sl,authorID,offset,scopus_machineID)
            publication['venue'] = find_publication_venue(soup[0])
            publication['keywords'] = find_publication_keywords(soup[0])
            date = soup[0].find("h2",text=re.compile("Abstract")).find_next("p").text
            publication['date'] = "-"
            publication['publications_cited'] = []
            publication['type'] = find_publication_type(soup[0])
            publication['citations'] = publication_citations

            authors = []
            all_authors = soup[0].find("p",id="authorlist").findAll("span")
            for author in all_authors:
                authors.append((author.find_next("a").text,"-"))
                
            publication['authors_affiliations'] = (authors,"-","-")   # also add the affiliation
            publications.append(publication)      

            return publications

        total_publications = soup[0].find("div",class_="resultsCountLabel").find("span",class_="resultsCount").text
       
        if total_publications < number_of_results:
            pages = 1
        else:
            pages = int(math.ceil(float(total_publications)/number_of_results))
        
        publication["subject_areas"] = find_subject_areas(author_url)
        publications.append(publication)
        publication = {}
        for each_page in range(0,pages): #(pages): 
            
            all_publications = soup[0].find("div",id="resultsBody").find("ul",id="documentListUl").findAll("li")
            
            for each_publication in all_publications:
               
                information_url = each_publication.find("span",class_="docTitle").find("a")["href"]
                new_soup = get_soup(information_url)
                publication_title = find_publication_title(each_publication)
                publication_citations = find_publication_citations(new_soup)
              
                duplicate_publication = check_database(publication_title,publication_citations,author,information_url)
                if duplicate_publication:    
                    print "ALREADY EXISTS"
                    continue        #ignore this publication and go to the next one
                
                print "NOT EXISTS scopus"
                publication['doi'] = find_publication_doi(publication_title)
                publication['title'] = publication_title
                publication['url'] = information_url
                publication['venue'] = find_publication_venue(new_soup)
                publication['keywords'] = find_publication_keywords(new_soup)
                publication['date'] = find_publication_date(each_publication)
                publication['publications_cited'] = find_publications_cited(each_publication,scopus_machineID)
                publication['type'] = find_publication_type(new_soup)
                publication['citations'] = publication_citations
                publication['authors_affiliations'] = find_authors_and_affiliations(each_publication,author,all_department_authors)
                publications.append(publication)

                publication = {}
                c = c + 1
                time.sleep(5)
                #print c
            time.sleep(5)  
            offset = offset + 20
            #author_url = "http://www.scopus.com/results/results.url?sort=plf-f&src=s&nlo=&nlr=&nls=&sid=C161EE2DDAD210425305FBA052E74B70.53bsOu7mi7A1NSY7fPJf1g%3a8830&sot=aut&sdt=a&sl=17&s=AU-ID%28{0}%29&cl=t&offset={1}&origin=resultslist&ss=plf-f&ws=r-f&ps=r-f&cs=r-f&cc=10&txGid=C161EE2DDAD210425305FBA052E74B70.53bsOu7mi7A1NSY7fPJf1g%3a993". format (authorID,offset)
            soup = get_author_soup(authorID,scopus_machineID,offset,sl) 
        
       
    except IndexError:
        print "index error"
        return publications
    except AttributeError:
        print "error start_crawling A"
        return publications     

    return publications
   

# if __name__ == '__main__':
#     c = 0
#     results = start_crawling("Manolis Vavalis")
#     if results != None:
#         for p in results:
#             print "---------------------------------"
#             print p
#             c = c + 1
#         print c
#     else:
#         print "there are no publications with this name"
