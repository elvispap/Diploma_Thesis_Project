import MySQLdb
# from geopy import geocoders 
import urllib,urllib2
import json
import socket
from pprint import pprint
import requests
from urllib2 import Request, urlopen, URLError, HTTPError
import base64
import urlparse
from bs4 import BeautifulSoup
import re
import time
# import mechanize
from contextlib import closing
# from selenium.webdriver import Firefox 
# from selenium.webdriver.support.ui import WebDriverWait
import math
from functools import wraps
import scopus
import difflib

execeptions = (socket.error,urllib2.HTTPError,urllib2.URLError)



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


def geocoding(affiliation):  
   
    quoted_query = urllib.quote(affiliation)
    url = "http://maps.googleapis.com/maps/api/geocode/json?address=%s" % quoted_query

    response = urllib2.Request(url)
    response.add_headers = [('User-agent', 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36')]
    jsongeocode = urllib2.urlopen(response)
    
    return jsongeocode

@retry(execeptions, tries=4, delay=10, backoff=3)
def find_publication_doi(title):

    try:
        opener = urllib2.build_opener()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36')]
        urllib2.install_opener(opener)
        new_title = title.replace(" ","+")
        url = "http://search.crossref.org/?q=%s&page=1&rows=1" % new_title
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

def remove_special_characters(string):
    all_chars = ['-','(',')','/','*',':','<','>','.',',']
    for char in all_chars:
        string = string.replace(char,' ')

    return string

""" Keep the lngthern part """
def similar(seq1, seq2):

    a = seq1.lower()
    b = seq2.lower()
    a_split = a.split(" ")
    b_split = b.split(" ")

    a_list_max = max(a_split, key=len)
    b_list_max = max(b_split, key=len)

    if a_list_max in b_split:
        return True
    if b_list_max in a_split:
        return True
 

    print difflib.SequenceMatcher(None, a, b).ratio()
    
    
    return difflib.SequenceMatcher(None, a, b).ratio() > 0.65

def aff_similar(seq1, seq2):

    a = seq1.lower()
    b = seq2.lower()

    if "university" in a:
        a = a.replace("university","")

    if "university" in b:
        b = b.replace("university","")

    a_split = a.split(" ")
    b_split = b.split(" ")

    a_list_max = max(a_split, key=len)
    b_list_max = max(b_split, key=len)

    if a_list_max in b_split:
        return True
    if b_list_max in a_split:
        return True
 

    print difflib.SequenceMatcher(None, a, b).ratio()
    
    
    return difflib.SequenceMatcher(None, a, b).ratio() > 0.65

def find_loc(affiliation):
    address = affiliation.replace("\n", "")
    result =  geocoding(address) 
    aff_location = ""
    country = ""
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
            print "error"
            aff_location = ""

    return [aff_location,country]

if __name__ == '__main__':

   

    connection = MySQLdb.connect(host="localhost",user="root",passwd="",db="uth_research_central_db")
    connection.set_character_set('utf8')
    x = connection.cursor()


    query = "SELECT * FROM `app_affiliation`"
    x.execute(query)
    row = x.fetchall()
    
    for i in row:   # for each co_author

        aff_id = i[0]
        
        x.execute("""INSERT INTO app_affiliation_department (affiliation_id,department_id) VALUES (%s,%s)""",[aff_id,"1"])
        connection.commit()

      
