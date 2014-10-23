import urllib
import urllib2
import urlparse
import time
import socket
import requests
from bs4 import BeautifulSoup
import re
import math
# import mechanize
import MySQLdb
from functools import wraps
import httplib

connection = MySQLdb.connect(host="localhost",user="root",passwd="********",db="uth_research_db")
connection.set_character_set('utf8')
cur = connection.cursor()

opener = urllib2.build_opener()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
# proxy = urllib2.ProxyHandler({'http': '120.198.243.151'})
# opener = urllib2.build_opener(proxy)
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36')]
urllib2.install_opener(opener)

execeptions = (socket.error,urllib2.HTTPError,urllib2.URLError,httplib.HTTPException)


def retry(ExceptionToCheck, tries=4, delay=15, backoff=3, logger=None):
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
     """ Used for removing some special characters from the giver string """
     
    all_chars = ['-','(',')','/','*',':','<','>','.',',']
    for char in all_chars:
        string = string.replace(char,' ')

    return string

@retry(execeptions, tries=4, delay=10, backoff=3)   
def find_publication_keywords(url):
    """ Find the publication's keywords """
    
    keywords = []
    try:
        htmltext = opener.open(url).read()
        soup = BeautifulSoup(htmltext)
        content = soup.find("div",id = "ctl00_divLeftWrapper")
        
        has_keywords = content.find("div",class_="section-wrapper").find("ul").findAll("li")
        for keyw in has_keywords:
            keyword = keyw.find("a").text.strip()
            keywords.append(' '.join(remove_special_characters(keyword.lower().strip()).split()))
            
        return keywords
        
    except AttributeError:
        print "error keywords"
        return keywords       #no keywords found
   




@retry(execeptions, tries=4, delay=10, backoff=3)
def find_publication_title(soup):
     """ Find the publication's title """
     
    try:
        title = soup.find("h3").find("a").text.strip()
        return ' '.join(remove_special_characters(title.capitalize().strip()).split())
    except AttributeError:
        return "-"       #no title found

@retry(execeptions, tries=4, delay=10, backoff=3)
def find_publication_url(soup):
     """ Find the publication's URL source """
    try:
        url = "http://academic.research.microsoft.com/" + soup.find("h3").find("a")["href"]      # the url of publication
        return url
    except AttributeError:
        return "-"       #no url found

@retry(execeptions, tries=4, delay=10, backoff=3)
def find_publication_citations(soup):
     """ Find the publication's number of citations """
     
    try:
        has_citations  = soup.find("span",class_="citation")
        citations = has_citations.find("a").text
        citatation_value = citations.split(" ")
        return citatation_value[1] 
    except AttributeError:
        return 0       


@retry(execeptions, tries=4, delay=10, backoff=3)
def find_publications_cited(soup):
    """ Find the publications which cite the given publication """
     
    publications = []
    try:
        
        has_citations  = soup.find("span",class_="citation")

        if has_citations != None:
            url = "http://academic.research.microsoft.com/" + has_citations.find_next("a")["href"]
            
            new_soup = get_soup(url)
            time.sleep(10)
            number_of_results = has_citations.find_next("a").text.split(":")[1].strip()
            if number_of_results > 10:
                pages = int(math.ceil(float(number_of_results)/10))
            else:
                pages = 1

            start = 1
            end = 10
            for each_page in range (0,pages): 
               
                all_publications = new_soup.findAll("li",class_="paper-item")
                for pub in all_publications:
                   
                    pub_title = find_publication_title(pub)
                    pub_url = find_publication_url(pub)
                    publications.append((pub_title,pub_url))
                    
                start = start + 10
                end = end + 10
               
                publications_url = url+"&start=%s&end=%s" % (start,end)
               
                time.sleep(10)
                new_soup = get_soup(publications_url)
            return publications
        
    except TypeError:
        print "type error"
        return publications
    except AttributeError:
        print "error publications cited"
        return publications


@retry(execeptions, tries=4, delay=10, backoff=3)
def find_authors_and_affiliations(soup,author_name,all_department_authors):
    """ Find the collaborated authors and theri affiliations for the giver publication """
    
    try:
    
        authors_affiliations = []
        author_last_name = author_name.split()[1]
        all_authors = soup.findAll("a",class_="author-name-tooltip")
        
        for author in all_authors:
            if author_last_name in author:
                continue
            author_name = remove_special_characters(author.text.strip())

            result = is_department_author(author_name,all_department_authors)    # check if the author is from the department
            if result:
                
                authors_affiliations.append((author_name,"","","department",result)) # remove pub_id
            else:
                
                author_url = author["href"]
                author_affiliation = find_affiliation(author_url)
                if author_affiliation == None:
                    authors_affiliations.append((author_name,"",author_url,"external"))
                else:
                    authors_affiliations.append((author_name,author_affiliation,author_url,"external"))

            time.sleep(10) 
        return authors_affiliations
    except AttributeError:
        print "error find_authors_and_affiliations"
        return authors_affiliations  

def is_department_author(author_name,all_department_authors):
    """ Check if a author is a author from the department """
    
    author_name_split = author_name.split(" ")
    author_name_list_max = max(author_name_split, key=len)
    for each_author in all_department_authors:
        if author_name_list_max in each_author[1]:
            author_id = each_author[0]
            return author_id
    return False  



@retry(execeptions, tries=4, delay=10, backoff=3)    
def find_affiliation(url):
     """ Find the publication's URL source """
     
    try:
        soup = get_soup(url)
        affiliation = soup.find("a",id="ctl00_MainContent_AuthorItem_affiliation").text.strip()
        return affiliation
    except AttributeError:
        print "No affiliation found"       
        return None


@retry(execeptions, tries=4, delay=20, backoff=3)
def get_soup(url):
  
    try:
        htmltext = opener.open(url).read()
        soup = BeautifulSoup(htmltext)
        return soup
    except AttributeError:
        print "none soup"
        return None      

@retry(execeptions, tries=4, delay=10, backoff=3)
def find_subject_areas(url):
    """ Find the subject area for the giver researcher (url) """
    sub_areas = []
    try:
        soup = get_soup(url)
        all_sub_areas = soup.findAll("div",class_="line-height-small")[1].findAll("a")
        for i in range(0,len(all_sub_areas)-1):
           sub_areas.append(remove_special_characters(all_sub_areas[i].text.strip()).strip())
        return sub_areas
    except AttributeError:
        return sub_areas

@retry(execeptions, tries=4, delay=10, backoff=3)
def find_publication_doi(title):
    """ Find the publication's doi """
    
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
            
            return new_doi[1]
        else:
            
            return doi.split("org/")[1]

    except AttributeError:
        print "error find doi"
        return ""
        
@retry(execeptions, tries=4, delay=10, backoff=3)
def find_type_date_venue(soup):
    """ Find the publication's type,date and venue """
    try:
        pub_type = "other"
        pub_date = "-"
        pub_venue = "-"

        has_venue = soup.findAll("div",class_="conference")
        all_divs = 0
        if has_venue != None :
            all_divs = len(has_venue)
            for venue in has_venue:
                is_empty = venue.find("span")
                if is_empty == None:
                    
                    all_divs = all_divs - 1
                    if all_divs == 0:       
                        pub_date = "-"
                        pub_venue = "-"
                        pub_type = "other"
                        break
                       
                    else:
                        continue
                
                conference = venue.find("span",id = re.compile("_txtConference"))
                if conference != None :
                    pub_type = "Conference"
                    conference_venue = venue.find("a",class_="conference-name")
                    pub_venue = conference_venue.text.strip()
                else:
                    journal = venue.find("span",id = re.compile("_txtJournal"))
                    if journal != None :
                        pub_type = "Journal"
                        journal_venue = venue.find("a",class_="conference-name")
                        pub_venue = journal_venue.text.strip()
                    else:
                        pub_type ="other"
                        pub_venue = "-"

                date = venue.find("span",class_="year")
                
                if date != None:
                    year_value = venue.find("span",class_="year").text.replace(",","").split(" ")
                    pub_date = year_value[len(year_value)-1]
                    if pub_date == "" or pub_date == 0:
                        pub_date = "-"
                    break
                else:
                    date = venue.find("span",id = re.compile("_lblYear"))
                    if date != None :
                        pub_date = date.text.split(" ")[2].replace(".","").strip()
                        if pub_date == "" or pub_date == 0:
                            pub_date = "-"
                        pub_venue = "-"
                        pub_type = "other"
                        break
                    else:
                        break
        
        else:
            pub_date = "-"
            pub_venue = "-"
            pub_type = "other"

        return [pub_date,pub_venue,pub_type]
    except AttributeError:
        print "error find_type_date_venue"
        return [pub_date,pub_venue,pub_type]


@retry(execeptions, tries=4, delay=10, backoff=3)
def check_database(title,citations,author_name):
""" Check the database if the current publication exists. If not, we check if its citations have changed and if yes,udpate the DB """

    try:
        query = "SELECT * FROM app_publication WHERE pub_title LIKE %s"
        cur.execute(query,["%" + title +"%"])
        connection.commit()
        row = cur.fetchall()
        if  row:    
            if int(citations) > int(row[0][6]):      # the citations of this publication have changed      
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
          
            return True          # there is a publication with this title,so ingore this publication
        else:
            return False        # there is not a publication with this title
    except AttributeError:
        print "AttributeError check db"
        return True

@retry(execeptions, tries=4, delay=10, backoff=3)
def start_crawling(author,authorID):
    """ Start the crawling proccess """
    try:
        publications = []
        publication = {}

        number_of_results = 100
        if authorID == None:
            return None
        author_url = "http://academic.research.microsoft.com/Author/%s" % authorID
        
        # find all the authors of the department 
        all_department_authors = []
        query = "SELECT * FROM app_author"
        cur.execute(query)
        row = cur.fetchall()
        for a in row:
            author_entry = (a[0],a[1])        # id + name
            all_department_authors.append(author_entry)
        
       
        soup = get_soup(author_url)
        time.sleep(10)  
        if soup == None :
            return None
        total_publications_0 = soup.find("a",id="ctl00_MainContent_PaperList_ctl00_HeaderLink").find("span",class_="item-count").text.strip().split(")")[0]
        total_publications = total_publications_0[1:]
       
        if total_publications < number_of_results:
            pages = 1
        else:
            pages = int(math.ceil(float(total_publications)/number_of_results))
        if pages == 0 :
            return None

        start = 1
        end = 100
        
        publications_url = "http://academic.research.microsoft.com/Detail?entitytype=2&searchtype=2&id={0}&start={1}&end={2}" . format (authorID,start,end)
        soup = get_soup(publications_url)
        
        time.sleep(10)  
        publication["subject_areas"] = find_subject_areas(author_url)
        publications.append(publication)
        publication = {}
       
        for each_page in range (0,pages): 
            
            all_publications = soup.findAll("li",class_="paper-item")
            for each_publication in all_publications:
                
                publication_title = find_publication_title(each_publication)
                publication_citations = find_publication_citations(each_publication)
               
                duplicate_publication = check_database(publication_title,publication_citations,author)
                if duplicate_publication == True:
                    print "ALREADY EXISTS"
                    continue        #ignore this publication and go to the next one
                print "NOT EXISTS microsoft"
                publication['title'] = publication_title
                publication['url'] = find_publication_url(each_publication)
                publication['citations'] = publication_citations
                time.sleep(10)
                publication['keywords'] = find_publication_keywords(publication['url'])
                publication['doi'] = find_publication_doi(publication_title)
                type_date_venue = find_type_date_venue(each_publication)
                publication['date'] = type_date_venue[0]
                publication['venue'] = type_date_venue[1]
                publication['type'] = type_date_venue[2]
                publication['publications_cited'] = find_publications_cited(each_publication) 
                publication['authors_affiliations'] = find_authors_and_affiliations(each_publication,author,all_department_authors) # remove publication_title
                publications.append(publication)
               
                time.sleep(10)
                publication = {}
                
            start = start + 100
            end = end + 100
            publications_url = "http://academic.research.microsoft.com/Detail?entitytype=2&searchtype=2&id={0}&start={1}&end={2}" . format (authorID,start,end)
            print "point 4"
            time.sleep(10)
            soup = get_soup(publications_url)
        
    except IndexError:
        print "IndexError"
        return publications
    except AttributeError:
        print "AttributeError"
        return publications   

    return publications
    
