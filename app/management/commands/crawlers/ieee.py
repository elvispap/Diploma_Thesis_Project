import urllib
import urllib2
import httplib
import time
import socket 
import MySQLdb
import urlparse
import datetime
from bs4 import BeautifulSoup
# import mechanize
import re
from ast import literal_eval
from itertools import takewhile
from bs4 import NavigableString
import math
from functools import wraps

#proxy = urllib2.ProxyHandler({'http': '87.200.21.203:80'})
opener = urllib2.build_opener()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36')]
urllib2.install_opener(opener)

execeptions = (socket.error,urllib2.HTTPError,urllib2.URLError,httplib.HTTPException)

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
def find_publication_citations(url):
    
    try:
        htmltext = opener.open(url).read()
        soup = BeautifulSoup(htmltext)
        metrics_tab_url = "http://ieeexplore.ieee.org/" + soup.find("div",id="nav-article").find("li",class_="active").find_next("a",id="abstract-metrics-tab")["href"]
        #print metrics_tab_url
        htmltext = opener.open(metrics_tab_url)
        soup = BeautifulSoup(htmltext)
        all_divs = soup.findAll("div",class_="art-cites-item")
        
        citations = []
        
        for each_div in all_divs:
            number_of_citations = each_div.find("span",class_="num").text.strip()
           
            citations.append(int(number_of_citations))
        if  citations:
            return max(citations)
        else:
            return 0
            
       
    except AttributeError:
        return 0
    except ValueError:
        return 0

@retry(execeptions, tries=4, delay=10, backoff=3)
def find_publications_cited(url):
    
    try:
        publications = []
        
        htmltext = opener.open(url).read()
        soup = BeautifulSoup(htmltext)
        cited_by_tab_url = "http://ieeexplore.ieee.org/" + soup.find("div",id="nav-article").find("a",id="abstract-citedby-tab")["href"]
        time.sleep(10)
        htmltext_2 = opener.open(cited_by_tab_url)
        soup_2 = BeautifulSoup(htmltext_2)
        all_pubs = soup_2.find("ol",id="Ieee_citations").findAll("li")
        for pub in all_pubs:
            
            link = "http://ieeexplore.ieee.org/" + pub.find("div",class_="links").find("a")["href"]
            time.sleep(10)
            htmltext_3 = opener.open(link)
            soup_3 = BeautifulSoup(htmltext_3)

            pub_title = remove_special_characters(soup_3.find("div",class_="title").find("h1").text.strip().capitalize())
            publications.append((pub_title,link))
            
        return publications
    except AttributeError:
        print "no cited"
        return publications
@retry(execeptions, tries=4, delay=10, backoff=3)
def find_publication_venue(url):
    
    try:
        htmltext = opener.open(url).read()
        soup = BeautifulSoup(htmltext)
        venue = soup.find("div",class_="article-ftr").find("a").text.strip()

        return venue
    except AttributeError:
        print "error_venue A"
        return "-"
   

@retry(execeptions, tries=4, delay=10, backoff=3)   
def find_publication_year_and_type( url):
    date = "-"
    type_of_pub = "-"
    try:
        htmltext = opener.open(url).read()
        soup = BeautifulSoup(htmltext)
        details = soup.find("div",class_="article-ftr")
        year_tag = details.findAll("h3")
        type_of_pub =  year_tag[1].text.split(" ")[2].split(":")[0]
        if type_of_pub == "Publication":
            type_of_pub = "Conference"
        date = year_tag[1].next_sibling.strip()
        new_date = date.split(" ")
        date = new_date[len(new_date)-1]
        if date == 0 or date == "":
            date = "-"
        return [date,type_of_pub]
    except AttributeError:
        return [date,type_of_pub]
    except IndexError:
        return [date,type_of_pub]
    

@retry(execeptions, tries=4, delay=10, backoff=3)
def find_publication_keywords(url):

    keywords = []
    try:
        htmltext = opener.open(url).read()
        soup = BeautifulSoup(htmltext)
        
        if soup ==None:
            print "no soup"
            return []   
        keywords_url = "http://ieeexplore.ieee.org/" + soup.find("a",id = "abstract-keyword-tab")["href"]
        if keywords_url == None:
            print "error url"
            return keywords
        time.sleep(10)
        
        htmltext = opener.open(keywords_url).read()
        soup = BeautifulSoup(htmltext)
        
        if soup == None:
            print "error soup keywords"
            return keywords

        has_indexed_keywords = soup.find("h2",text=re.compile("INSPEC: CONTROLLED INDEXING"))   #INSPEC: CONTROLLED INDEXING
        
        if has_indexed_keywords != None:
            author_keywords = has_indexed_keywords.find_next("ul").findAll("li")
            for keyword in author_keywords:
                keyword_value = keyword.find("a").text.strip()
                keywords.append(' '.join(remove_special_characters(keyword_value.lower()).split()))  

        has_ieee_keywords = soup.find("h2",text=re.compile("IEEE TERMS"))   #IEEE INDEXING

        if has_ieee_keywords != None:

            author_keywords = has_ieee_keywords.find_next("ul").findAll("li")    
            for keyword in author_keywords:
                keyword_value = keyword.find("a").text.strip()
                keywords.append(' '.join(remove_special_characters(keyword_value.lower()).split()))

        return keywords
        
    except AttributeError:
        print "error keywords A"
        return keywords       #no keywords found
    except IndexError:
        print "error keywords I"
        return keywords       #no keywords found
    except TypeError:
        print "type error"
        return keywords

@retry(execeptions, tries=4, delay=10, backoff=3)
def find_publication_url(soup):
    try:
        url = "http://ieeexplore.ieee.org/" + soup.find_next("a")["href"]      # the url of publication
        return url
    except AttributeError:
        return "-"      

@retry(execeptions, tries=4, delay=10, backoff=3)       
def find_publication_title(soup):

    try:
        title = soup.find_next("h3").find("a").text.strip()               # the title of publication
        return ' '.join(remove_special_characters(title.capitalize()).split()) 
    except AttributeError:
        return "-"      

@retry(execeptions, tries=4, delay=10, backoff=3) 
def find_publication_authors(soup,author_name):

    try:
        author_last_name = author_name.split()[1]
        authors = []
        all_authors = soup.findAll("span",id="preferredName")
        for i in range(0, len(all_authors)):
            author_name = remove_special_characters(soup.findAll("span",id="preferredName")[i].text.strip())
            if author_last_name in author_name:
                continue
            else:
                authors.append(author_name) 
        return authors
    except AttributeError:
        return []      

@retry(execeptions, tries=4, delay=10, backoff=3) 
def find_affiliations(soup):
    
    try:
        affilations = []
        all_affilations = soup.find("ul",id="Affiliation-refinements").findAll("li")
        for affiliation in all_affilations:
            value = affiliation.find("span",class_="refinement").text.strip()
            value_2 = value.replace("(1)"," ").replace("(2)"," ").replace("\t"," ").replace("\r\n"," ").strip()
            #value = affiliation.text.strip().lstrip().rstrip()
            if not "Thessaly" in value_2:
                affilations.append(value_2)
            
        return affilations
    except AttributeError:
        return affilations      #no affiliation found     

@retry(execeptions, tries=4, delay=10, backoff=3)
def get_soup(author,page):
    
    try:
        
        author_name = author.split()
        rows = 25
        
        # if len(author_name) == 1:
        #   url = "http://ieeexplore.ieee.org/search/searchresult.jsp?\searchWithin=p_Last_Names:%s&matchBoolean=true&queryText=(p_Authors:%s)&rowsPerPage=%s&pageNumber=%s&resultAction=ROWS_PER_PAGE" % (author_name[0],author_name[0], rows, page)
        # else:   
        #url = "http://ieeexplore.ieee.org/search/searchresult.jsp?searchWithin=p_First_Names:%s&searchWithin=p_Last_Names:%s&matchBoolean=true&queryText=(p_Authors:%s,+%s)&rowsPerPage=%s&pageNumber=%s&resultAction=ROWS_PER_PAGE" % (author_name[0],author_name[1], author_name[0], author_name[1], rows, page)
        new_url = "http://ieeexplore.ieee.org/search/searchresult.jsp?queryText%3D{0}+{1}&pageNumber={2}" . format(author_name[0],author_name[1],page)
        htmltext = opener.open(new_url).read()
        soup = BeautifulSoup(htmltext)
        return soup
    # except socket.error:
    #   print "error soup"
    #   return None
    except AttributeError:
        print "error soup A"
        return None


@retry(execeptions, tries=4, delay=10, backoff=3)
def check_database(title,citations,author_name):
    """ Check the database if the current publication exists. If not, we check if its citations have changed and if yes,udpate the DB """
    try:
        connection = MySQLdb.connect(host="localhost",user="root",passwd="********",db="uth_research_db")
        connection.set_character_set('utf8')
        cur = connection.cursor()
      
        query = "SELECT * FROM app_publication WHERE pub_title LIKE %s"
        cur.execute(query,["%" + title +"%"])
        connection.commit()
        row = cur.fetchall()
        if  row:    
            if int(row[0][6]) < int(citations):
           
                cur.execute("""UPDATE app_publication SET pub_citations=%s WHERE pub_title=%s""",[citations,title])
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
          
            return True         # there is a publication with this title,so ingore this publication
        else:
          
            return False        # there is a publication with this title,so ingore this publication
       
            #############################################################################

            # if publications_cited:
            #     for pub in publications_cited:
            #         pub_cited_title = pub[0]
            #         pub_cited_url = pub[1]

            #         query = "SELECT * FROM app_publication_cited WHERE pub_title LIKE %s"
            #         cur.execute(query,["%" + pub_cited_title +"%"])
            #         row = cur.fetchall()
            #         if  row:   # exists
            #             pub_citedID = row[0][0]
                       
            #         else:       # not exists
            #             print "write to app_publication_cited"
            #             cur.execute("""INSERT INTO app_publication_cited (pub_title,pub_url) VALUES (%s,%s)""",[pub_cited_title,pub_cited_url])
            #             pub_citedID = cur.lastrowid
            #             connection.commit()

            #             # update also the entry in central database
            #             connection_2 = MySQLdb.connect(host="localhost",user="root",passwd="",db="uth_research_central_db")
            #             connection_2.set_character_set('utf8')
            #             x = connection_2.cursor()
            #             x.execute("""INSERT INTO app_publication_cited (pub_title,pub_url) VALUES (%s,%s)""",[pub_cited_title,pub_cited_url])
            #             pub_citedID = x.lastrowid
            #             connection_2.commit()


            #         query = "SELECT * FROM app_publication_publication_cited WHERE publication_id = %s AND publication_cited_id = %s"
            #         cur.execute(query,[pub_id,pub_citedID])
            #         row = cur.fetchall()
            #         if not row:
            #             print "write to app_publication_publication_cited"
            #             cur.execute("""INSERT INTO app_publication_publication_cited (publication_id,publication_cited_id) VALUES (%s,%s)""",[pub_id,pub_citedID])
            #             connection.commit()
            #############################################################################

            
     
    except AttributeError:
        print "AttributeError check db"
        return True

@retry(execeptions, tries=4, delay=10, backoff=3)
def find_publication_doi(title):

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
            #print new_doi[1]
            return new_doi[1]
        else:
            #print doi.split("org/")[1]
            return doi.split("org/")[1]

    except AttributeError:
        print "no doi"
        return ""

@retry(execeptions, tries=4, delay=10, backoff=2)   
def start_crawling(author,name_to_search):

    number_of_results = 25
    publications = []       # a dictionary for saving all publication of the author
    publication = {}
    try :
        if name_to_search != "":
            author = name_to_search

        soup = get_soup(author, 1)
        if soup == None:
            return None
       
        total_publications = soup.find("div",id="content").find("span",class_="results-returned").text.split(" ")[0]
        if total_publications < number_of_results:
            pages = 1
        else:
            pages = int(math.ceil(float(total_publications)/number_of_results))

        if pages == 0 :
            return None
            
        affilations = find_affiliations(soup)
        publication['affiliations'] = affilations       # save the dictionary at the start of the list
        publications.append(publication)
        publication = {}
        for each_page in range(2, int(pages)+2):   #range (int(pages)+1)  
            #time.sleep(15)
            all_publications = soup.findAll("li",class_="noAbstract")
            
            for each_publication in all_publications:
               
                publication['url'] = find_publication_url(each_publication)
                publication_title = find_publication_title(each_publication)
               
                publications_citations = find_publication_citations(publication['url'])
                time.sleep(5)
               
                duplicate_publication = check_database(publication_title,publications_citations,author)
                if duplicate_publication == True:
                    print "ALREADY EXISTS"
                    continue        #ignore this publication and go to the next one
                print "NOT EXISTS ieee"

                publication['doi'] = find_publication_doi(publication_title)
                publication['title'] = publication_title
                publication['venue'] = find_publication_venue(publication['url'])
                publication['keywords'] = find_publication_keywords(publication['url'])
                publication['publications_cited'] = find_publications_cited(publication['url'])
                date_and_type = find_publication_year_and_type(publication['url'])
                publication['date'] = date_and_type[0].strip()
                publication['type'] = date_and_type[1].strip()
                time.sleep(5)
                publication['citations'] = publications_citations
                publication['authors'] = find_publication_authors(each_publication,author) 
                #time.sleep(20)
                publications.append(publication)
                
                publication = {}
                 
            time.sleep(5)
            soup = get_soup(author,each_page)
       
    except IndexError:
        print "index error"
        return publications
    except AttributeError:
        print "error start_crawling A"
        return publications     

    return publications

# if __name__ == '__main__':
#     results = start_crawling("Dimitrios Katsaros")
#     c = 0
#     if results!=None:
#         for i in results :
#             print i
#             print "*************************"
#             c = c + 1
#     
