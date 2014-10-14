from django.http import HttpResponse
from django.shortcuts import render
from django.http import Http404
from app.models import *
from django.db.models import Q
from django.db.models import Sum
import json
import xml.etree.cElementTree as ET
from  __builtin__ import any as b_any
import datetime
import time
from django.http import HttpResponseRedirect
import os.path
import difflib
import MySQLdb
from django.contrib.staticfiles import finders


def find_affiliations(not_rest_affs,src):

    affiliations = []
    all_affiliations = []
    
    all_entries = affiliation.objects.all()
    for entry in all_entries:
       
        affiliation_location = entry.affiliation_location

        if affiliation_location == "":
            continue
        
        affil = {}
        affiliation_name = entry.affiliation_name
        affiliation_id = entry.id    
        #and check_affs(affiliation_name,not_rest_affs) 
        if affiliation_name not in affiliations and affiliation_name != "" and check_affs(affiliation_name,not_rest_affs):#and not check_for_dublicates(affiliation_name,affiliations):
           
            #aff = affiliation.objects.get(affiliation_name = affiliation_name)
            affiliations.append(affiliation_name)
            affiliation_weight = co_author_affiliation.objects.filter(affiliation_id = affiliation_id)
            if len(affiliation_weight) == 0:
                continue
            if src == "access_db":
                affil["affiliation_name"] = affiliation_name
            else:
                affil["weight"] = len(affiliation_weight)
                affil["affiliation_name"] = affiliation_name
            affil["affiliation_location"] = affiliation_location
            affil["affiliation_id"] = affiliation_id
            
        else:
            continue  
        all_affiliations.append(affil)
    if src == "access_db":
        data = sorted(all_affiliations, key=lambda k: k['affiliation_name'],reverse=True)
        return data
    else:
        data = sorted(all_affiliations, key=lambda k: k['weight'],reverse=True)
        new_data = []
        for item in data:
            affil_new = {}
            aff_weight =  item["weight"]
            aff_name = item["affiliation_name"]
            aff_location = item["affiliation_location"]
            aff_id = item["affiliation_id"]
            affil_new["affiliation_name"] = "("+str(aff_weight)+")" + aff_name
            affil_new["affiliation_location"] = aff_location
            affil_new["affiliation_id"] = aff_id
            new_data.append(affil_new) 

        return new_data

def find_affiliations_central_page(not_rest_affs):

    affiliations = []
    all_affiliations = []
    
    all_entries = affiliation.objects.all()
    for entry in all_entries:
       
        affiliation_location = entry.affiliation_location

        if affiliation_location == "":
            continue
        
        affil = {}
        affiliation_name = entry.affiliation_name
        affiliation_id = entry.id    
        #and check_affs(affiliation_name,not_rest_affs) 
        if affiliation_name not in affiliations and affiliation_name != "" and check_affs(affiliation_name,not_rest_affs):#and not check_for_dublicates(affiliation_name,affiliations):
           
            #aff = affiliation.objects.get(affiliation_name = affiliation_name)
            affiliations.append(affiliation_name)
            affiliation_weight = co_author_affiliation.objects.filter(affiliation_id = affiliation_id)
            if len(affiliation_weight) == 0:
                continue
            if src == "access_db":
                affil["affiliation_name"] = affiliation_name
            else:
                affil["weight"] = len(affiliation_weight)
                affil["affiliation_name"] = affiliation_name
            affil["affiliation_location"] = affiliation_location
            affil["affiliation_id"] = affiliation_id
            
        else:
            continue  
        all_affiliations.append(affil)
    
        data = sorted(all_affiliations, key=lambda k: k['affiliation_name'],reverse=True)
        return data
    
   
def check_for_dublicates(aff,aff_list):

    a = aff.lower()
    if "university" in a:
        a = a.replace("university","")

    a_split = a.split(" ")
    a_max = max(a_split, key=len)

    seq2_lower = [x.lower() for x in aff_list]

    for element in seq2_lower:
        element_split = element.split(" ")
        element_max = max(element_split, key=len)
        if element_max in a_split or a_max in element:
            return True
    
    for element in seq2_lower:
        if difflib.SequenceMatcher(None, element, a).ratio() > 0.75:
            return True
    return False

def check_affs(affiliation,affiliations):

    affiliation_parts = affiliation.replace(",", "")
    all_parts = affiliation_parts.split()
    for part in all_parts:
        if part in affiliations:
            return False
        
    return True


def central_page(request):         # ONLY CENTRAL PAGE EDITION

    connection = MySQLdb.connect(host="localhost",user="root",passwd="",db="uth_research_central_db")
    connection.set_character_set('utf8')
    cur = connection.cursor()

    query = "SELECT * FROM app_publication"
    cur.execute(query)
    all_pubs = cur.fetchall()
    total_publications = 0
    total_citations = 0

    eece_total_publications = 0
    eece_total_citations = 0
    me_total_publications = 0
    me_total_citations = 0
    prd_total_publications = 0
    prd_total_citations = 0
    cv_total_publications = 0
    cv_total_citations = 0
    ae_total_publications = 0
    ae_total_citations = 0

    for pub in all_pubs:
        total_publications = total_publications + 1
        total_citations = total_citations + pub[6]
        if pub[8] == "Electrical and Computer Engineering":
            eece_total_publications =  eece_total_publications + 1
            eece_total_citations =  eece_total_citations + pub[6]
        elif pub[8] == "Mechanical Engineering":
            me_total_publications =  me_total_publications + 1
            me_total_citations =  me_total_citations + pub[6]
        elif pub[8] == "Planning and Regional Development":
            prd_total_publications =  prd_total_publications + 1
            prd_total_citations =  prd_total_citations + pub[6]
        elif pub[8] == "Civil Engineering":
            cv_total_publications =  cv_total_publications + 1
            cv_total_citations =  cv_total_citations + pub[6]
        elif pub[8] == "Architecture Engineering":
            ae_total_publications =  ae_total_publications + 1
            ae_total_citations =  ae_total_citations + pub[6]

    all_subject_araes = []
    query = "SELECT * FROM app_subject_area"
    cur.execute(query)
    all_sub_a = cur.fetchall()
    for sub_a in all_sub_a:
        all_subject_araes.append(sub_a[1])
    
    not_rest_affs = ["Thessaly","thessaly","volos","Volos"]     # must be dynamic
  
    departements = []
    query = "SELECT * FROM app_departments"
    cur.execute(query)
    all_deps = cur.fetchall()
    for dep in all_deps:
        d = {}
        d["name"] = dep[1]
        
        if dep[1] == "Electrical and Computer Engineering":
            d["total_publications"] = eece_total_publications
            d["total_citations"] = eece_total_citations
            d["logo"] = dep[1].lower().replace(" ","_")
            d["url"] = "eece"

        elif dep[1] == "Mechanical Engineering":
            d["total_publications"] = me_total_publications
            d["total_citations"] = me_total_citations
            d["logo"] = dep[1].lower().replace(" ","_")
            d["url"] = "#"
        elif dep[1] == "Planning and Regional Development": 
            d["total_publications"] = prd_total_publications
            d["total_citations"] = prd_total_citations
            d["logo"] = dep[1].lower().replace(" ","_")
            d["url"] = "#"
        elif dep[1] == "Civil Engineering":
            d["total_publications"] = cv_total_publications
            d["total_citations"] = cv_total_citations
            d["logo"] = dep[1].lower().replace(" ","_")
            d["url"] = "#"
        elif dep[1] == "Architecture Engineering": 
            d["total_publications"] = ae_total_publications
            d["total_citations"] = ae_total_citations
            d["logo"] = dep[1].lower().replace(" ","_")
            d["url"] = "#"

        departements.append(d)
        not_rest_affs = ["Thessaly","thessaly","volos","Volos"]     # must be dynamic
        all_affiliations = find_affiliations(not_rest_affs,"null")
        query = "SELECT DISTINCT(affiliation_country) AS affiliation_country FROM app_affiliation ORDER BY affiliation_country DESC"
        cur.execute(query)
        total_countries = cur.rowcount
   
    return render(request, 'index_central.html',{'total_publications':total_publications,'total_citations':total_citations,'total_countries':total_countries,'affiliations':all_affiliations,'subject_areas':len(all_subject_araes),'departements':departements})
    
def home(request):

    total_publications = publication.objects.count()
   
    all_subject_areas = subject_area.objects.count()
    total_keywords = keyword.objects.all()
    not_rest_affs = ["Thessaly","thessaly","volos","Volos"]     # must be dynamic
    all_affiliations = find_affiliations(not_rest_affs,"null")
    total_countries = affiliation.objects.values_list("affiliation_country").distinct()
    total_citations = publication.objects.aggregate(Sum('pub_citations'))["pub_citations__sum"]
    logo = department_logo.objects.get(id=1)
   
    return render(request, 'index.html',{'total_publications':total_publications,'total_citations':total_citations,'total_countries':len(total_countries),'affiliations':all_affiliations,'keywords':total_keywords,'subject_areas':all_subject_areas,'department_logo':logo})

def home_search_by_keyword(request):

    keyWord = request.GET["keyword_to_search"]
    keyw = keyWord.replace("_"," ")
    try:
        k = keyword.objects.get(keyword = keyw)
    except keyword.DoesNotExist:
        return render(request, 'publications_search_results.html',{'results':[],'keyword':"",'home_search_by_keyword':True})
    keywordID = k.id
   
    data_to_return = []
    all_pubs = []
    
    all_entries = keyword_publication.objects.filter(keyword_id = keywordID)   
    for entry in all_entries:
        pub_id = entry.publication_id
        p = publication.objects.get(id = pub_id)

        # find the publication's keywords
        pub_keywords = []
        all_pubs = keyword_publication.objects.filter(publication_id = pub_id)
        for pub in all_pubs:                            # loop through all publications's keywords ids
            pub_keyw_id = keyword.objects.get(id = pub.keyword_id)
            if pub_keyw_id.keyword not in pub_keywords:
                pub_keywords.append(pub_keyw_id.keyword)


        # find the publication's external authors
        pub_co_authors = []
        all_co_authors = publication_co_author.objects.filter(publication_id = pub_id)
        for a in all_co_authors:
            co_author_entry = co_author.objects.get(id = a.co_author_id)
            co_author_name = co_author_entry.name.replace(",","")
            co_author_profile_url = co_author_entry.profile_url
            #co_author_affiliation = co_author_entry.affiliation
            pub_co_authors_dict = {}
            if co_author_name not in pub_co_authors:
                pub_co_authors_dict["name"] = co_author_name
                pub_co_authors_dict["profile_url"] = co_author_profile_url
                pub_co_authors.append(pub_co_authors_dict)

        # find the publication's inernal authors
        pub_authors = []
        all_authors = publication_author.objects.filter(publication_id = pub_id)
        for a in all_authors:
            author_entry = author.objects.get(id = a.author_id)
            author_name = author_entry.name.replace(",","")
            author_profile_url = "/authors/%s" % author_name.replace(" ","_")
            #co_author_affiliation = co_author_entry.affiliation
            pub_authors_dict = {}
            if author_name not in pub_co_authors:
                pub_authors_dict["name"] = author_name
                pub_authors_dict["profile_url"] = author_profile_url
                pub_co_authors.append(pub_authors_dict)

        publication_dict = {}
        publication_dict["title"] = p.pub_title
        publication_dict["url"] = p.pub_url
        publication_dict["venue"] = p.pub_venue
        publication_dict["date"] = p.pub_date
        publication_dict["type"] = p.pub_type
        publication_dict["doi"] = p.pub_doi
        publication_dict["citations"] = p.pub_citations
        publication_dict["keywords"] = pub_keywords
        publication_dict["co_authors"] = pub_co_authors
        ########################################################################################
        pubs_cited = publication_publication_cited.objects.filter(publication_id = pub_id)
        cited_doc = []
        all_cited_pub_ids = []
        for pub in pubs_cited:
            if pub.publication_cited_id not in all_cited_pub_ids:
                all_cited_pub_ids.append(pub.publication_cited_id)
                doc = publication_cited.objects.get(id = pub.publication_cited_id)
                cited_doc.append([doc.pub_title,doc.pub_url])
        publication_dict["publications_cited"] = cited_doc
        ########################################################################################
        data_to_return.append(publication_dict) 

    sorted_data = sorted(data_to_return, key=lambda k: k['date'],reverse=True) 
    return render(request, 'publications_search_results.html',{'results':sorted_data,'keyword':keyw.strip(),'home_search_by_keyword':True})
    
def publications(request):

    
    all_keyws_ids = []
    keyws_ids = []
    keywords = []
   
    all_keywords = keyword.objects.count()
    top_keywords = keyword.objects.order_by('-freq')[:10]
   
    all_authors = author.objects.all();
    top_publications = publication.objects.order_by('-pub_citations')
    all_keywords = keyword.objects.all()
    

    return render(request, 'publications.html',{'top_publications':top_publications[0:5],'keywords':all_keywords,'top_keywords':top_keywords,'authors':all_authors,'max_citations':top_publications[0].pub_citations})

def all_publications(request):      # ONLY CENTRAL PAGE EDITION
   
    connection = MySQLdb.connect(host="localhost",user="root",passwd="",db="uth_research_central_db")
    connection.set_character_set('utf8')
    cur = connection.cursor()

    query = "SELECT * FROM app_publication"
    cur.execute(query)
    publications = cur.fetchall()

    results = []
    for pub in publications:

        publication_dict = {}
        publication_dict["title"] = pub[1]
        publication_dict["url"] = pub[2]
        publication_dict["venue"] = pub[3]
        publication_dict["date"] = pub[4]
        publication_dict["type"] = pub[5]
        publication_dict["citations"] = pub[6]
        publication_dict["doi"] = pub[7]
        
        
        results.append(publication_dict) 

    data = sorted(results, key=lambda k: k['date'],reverse=True) 
    return render(request, 'all_publications.html',{'results':data})
   
def citations(request):

    all_citations = publication_cited.objects.all()
    
    return render(request, 'citations.html',{'citations':all_citations})

def all_citations(request):     # ONLY CENTRAL EDITION 

    connection = MySQLdb.connect(host="localhost",user="root",passwd="",db="uth_research_central_db")
    connection.set_character_set('utf8')
    cur = connection.cursor()

    query = "SELECT * FROM app_publication_cited"
    cur.execute(query)
    all_pubs_cited = cur.fetchall()
    all_citations = []
    
    for pub in all_pubs_cited:
        p = {}
        p["pub_title"] = pub[1]
        p["pub_url"] = pub[2]
        all_citations.append(p)
    return render(request, 'all_citations.html',{'citations':all_citations})

def collaborations(request):

    not_rest_affs = ["Thessaly","thessaly","volos","Volos"]     # must be dynamic
    all_affiliations = find_affiliations(not_rest_affs,"null")
    
    return render(request, 'collaborations.html',{'affiliations':all_affiliations})

def find_common_elements(list1,list2):
    """ Find the common elements from list1 and list2 """

    if not list1:
        return list2
    elif not list2:
        return list1
    else:
        return set(list1) & set(list2)

def check_if_exists(author_name):
    """  Find if exists an author with the given name """
    try:
        result = author.objects.get(name = author_name)
        return True
    except author.DoesNotExist:
        return False


def publications_search(request):

    if request.method == "GET":

        results = []
        publications_to_return = []
        keyws_pubs_ids = []
        authors_pubs_ids = []        
        all_keywords = []
        all_authors = []

        doc_title = request.GET["doc_title"]
        doc_keywords = request.GET["keywords"]
        doc_authors = request.GET["authors"]

        max_citations = False
        if request.GET["number_of_citations"]:
            number_of_citations = request.GET["number_of_citations"]
            max_citations = True
        
        conference = False
        journal = False
        book = False
        other = False
        ex_year_from = False
        ex_year_to = False

        doc_type = request.GET["doc_type"]
        
        if doc_type == "Conference":
            conference = True
        elif doc_type == "Journal":
            journal = True
        elif doc_type == "Book":
            book = True
        elif doc_type == "Other":
            other = True
       
        if "doc_year_from" in request.GET:
            year_from = request.GET["doc_year_from"]
            if year_from == "":
                ex_year_from = False
            else:
                ex_year_from = True
        if "doc_year_to" in request.GET:
            year_to = request.GET["doc_year_to"]
            if year_to == "":
                ex_year_to = False
            else:
                ex_year_to = True
        
        if doc_keywords:
            all_keywords = doc_keywords.split(",")
            
            for keyw in all_keywords:
                if keyw != "":
                    keyw_entry = keyword.objects.get(keyword = keyw).id
                    keyw_pubs = keyword_publication.objects.filter(keyword_id = keyw_entry)
                    for keyw_pub in keyw_pubs:
                        pub_id = publication.objects.get(id = keyw_pub.publication_id).id
                        if pub_id not in keyws_pubs_ids:
                            keyws_pubs_ids.append(pub_id)
        if doc_authors:
            all_authors = doc_authors.split(",")

            for auth in all_authors:
                if auth != "" and check_if_exists(auth):
                    author_entry = author.objects.get(name = auth).id
                    author_pubs = publication_author.objects.filter(author_id = author_entry)
                    for author_pub in author_pubs:
                        pub_id = publication.objects.get(id = author_pub.publication_id).id
                        if pub_id not in authors_pubs_ids:
                            authors_pubs_ids.append(pub_id)
                       

        pubs_common_ids = find_common_elements(keyws_pubs_ids,authors_pubs_ids)
       
        if doc_title:
            entries = publication.objects.filter(pub_title__contains = doc_title)
            pubs_ids = []
            for entry in entries:
                if entry.id not in pubs_ids:
                    pubs_ids.append(entry.id)
            pubs_common_ids = find_common_elements(pubs_common_ids,pubs_ids)

        if conference:
            entries = publication.objects.filter(pub_type = "Conference")
            pubs_ids = []
            for entry in entries:
                if entry.id not in pubs_ids:
                    pubs_ids.append(entry.id)
            pubs_common_ids = find_common_elements(pubs_common_ids,pubs_ids)

            
        elif journal:
            entries = publication.objects.filter(pub_type = "Journal")
            pubs_ids = []
            for entry in entries:
                if entry.id not in pubs_ids:
                    pubs_ids.append(entry.id)
            pubs_common_ids = find_common_elements(pubs_common_ids,pubs_ids)
        elif book:
            entries = publication.objects.filter(pub_type = "Book")
            pubs_ids = []
            for entry in entries:
                if entry.id not in pubs_ids:
                    pubs_ids.append(entry.id)
            pubs_common_ids = find_common_elements(pubs_common_ids,pubs_ids)
        elif other:
            entries = publication.objects.filter(pub_type = "other")
            pubs_ids = []
            for entry in entries:
                if entry.id not in pubs_ids:
                    pubs_ids.append(entry.id)
            pubs_common_ids = find_common_elements(pubs_common_ids,pubs_ids)

        if max_citations:
            entries = publication.objects.filter(pub_citations__gte = number_of_citations)
            pubs_ids = []
            for entry in entries:
                if entry.id not in pubs_ids:
                    pubs_ids.append(entry.id)
            pubs_common_ids = find_common_elements(pubs_common_ids,pubs_ids)

        if ex_year_from:
            entries = publication.objects.filter(pub_date__gte = year_from)
            pubs_ids = []
            for entry in entries:
                if entry.id not in pubs_ids:
                    pubs_ids.append(entry.id)
            pubs_common_ids = find_common_elements(pubs_common_ids,pubs_ids)
            HttpResponse(pubs_common_ids)
        if ex_year_to:
            entries = publication.objects.filter(pub_date__lte = year_to)
            pubs_ids = []
            for entry in entries:
                if entry.id not in pubs_ids:
                    pubs_ids.append(entry.id)
            pubs_common_ids = find_common_elements(pubs_common_ids,pubs_ids)

        for pub_id in pubs_common_ids:
            publications = publication.objects.filter(id = pub_id)
            
            for pub in publications:

                # find the publication's keywords
                pub_keywords = []
                pubs_keyws = keyword_publication.objects.filter(publication_id = pub.id)
                for pub_keyw in pubs_keyws:            
                    pub_keyw_id = keyword.objects.get(id = pub_keyw.keyword_id)
                    if pub_keyw_id.keyword not in pub_keywords:
                        pub_keywords.append(pub_keyw_id.keyword)

                # find the publication's co authors 
                pub_co_authors = []
                pub_co_authors_names = []
                
                all_entries = publication_co_author.objects.filter(publication_id = pub.id)
                for each_entry in all_entries:             
                    co_auth = co_author.objects.get(id = each_entry.co_author_id)
                    if co_auth.name not in pub_co_authors_names:
                        pub_co_authors_dict = {}
                        pub_co_authors_names.append(co_auth.name)
                        pub_co_authors_dict["name"] = co_auth.name
                        pub_co_authors_dict["profile_url"] = co_auth.profile_url
                        pub_co_authors.append(pub_co_authors_dict)

                # find the publication's inernal authors
                pub_authors = []
                all_int_authors = publication_author.objects.filter(publication_id = pub.id)
                for a in all_int_authors:
                    author_entry = author.objects.get(id = a.author_id)
                    author_name = author_entry.name.replace(",","")
                    author_profile_url = "/authors/%s" % author_name.replace(" ","_")
                    #co_author_affiliation = co_author_entry.affiliation
                    pub_authors_dict = {}
                    if author_name not in pub_co_authors:
                        pub_authors_dict["name"] = author_name
                        pub_authors_dict["profile_url"] = author_profile_url
                        pub_co_authors.append(pub_authors_dict)

                publication_dict = {}
                publication_dict["title"] = pub.pub_title
                publication_dict["url"] = pub.pub_url
                publication_dict["venue"] = pub.pub_venue
                publication_dict["date"] = pub.pub_date
                publication_dict["type"] = pub.pub_type
                publication_dict["doi"] = pub.pub_doi
                publication_dict["citations"] = pub.pub_citations
                publication_dict["keywords"] = pub_keywords
                publication_dict["co_authors"] = pub_co_authors
                ########################################################################################
                pubs_cited = publication_publication_cited.objects.filter(publication_id = pub_id)
                cited_doc = []
                all_cited_pub_ids = []
                for pub in pubs_cited:
                    if pub.publication_cited_id not in all_cited_pub_ids:
                        all_cited_pub_ids.append(pub.publication_cited_id)
                        doc = publication_cited.objects.get(id = pub.publication_cited_id)
                        cited_doc.append([doc.pub_title,doc.pub_url])
                publication_dict["publications_cited"] = cited_doc
                ########################################################################################
                results.append(publication_dict) 

     

        data = sorted(results, key=lambda k: k['date'],reverse=True) 
        return render(request, 'publications_search_results.html',{'results':data,'all_keywords':all_keywords,'doc_title':doc_title,
            'conference':conference,'journal':journal,'book':book,'other':other,'max_citations':max_citations,'ex_year_from':ex_year_from,
            'ex_year_to':ex_year_to})
    else:
        return render(request,'error_404.html')

def authors(request):
   
    data_to_return = []
    author_dict = {}
    all_authors = author.objects.all()
    for each_author in all_authors:
        author_name = each_author.name
        authorId = each_author.id

        pub_co_authors = []

        total_publications = publication_author.objects.filter(author_id = authorId)
        citations = 0
        for each_publication in total_publications:
            pub = publication.objects.get(id = each_publication.publication_id)
            citations = citations + pub.pub_citations

            #find the co authors
            # all_co_authors = publication_co_author.objects.filter(publication_id = each_publication.publication_id)
            # for a in all_co_authors:
            #     co_author_entry = co_author.objects.get(id = a.co_author_id)
            #     co_author_name = co_author_entry.name.replace(",","")
            #     if co_author_name not in pub_co_authors:
            #         pub_co_authors.append(co_author_name)
                
        author_dict["name"] = author_name
        author_dict["total_publications"] = len(total_publications)
        author_dict["total_citations"] = citations
        autor_name = author_name.lower().replace(" ","_")
        if finders.find('img/photo_profile/'+autor_name+'.jpg'):        # check if image profile exists 
            author_dict["photo_profile_name"] = autor_name   
        else:
            author_dict["photo_profile_name"] = "-"   
     
        data_to_return.append(author_dict)
        author_dict = {}
    sorted_data = sorted(data_to_return, key=lambda k: k['name']) 
    #all_citations = publication.objects.aggregate(Sum('pub_citations'))["pub_citations__sum"]
    #all_publications = publication.objects.count()
    return render(request, 'authors.html',{'authors':sorted_data})

def my_custom_404_view(request):
    return render(request, 'error_404.html')

def my_custom_500_view(request):
    return render(request, 'error_500.html')

def publications_keyword(request,keyWord):
    
    keyw = keyWord.replace("_"," ") 
    try: 
        k = keyword.objects.filter(keyword = keyw)[:1].get()    # FIX IT FOR DUPLICATES 
        keywordID = k.id
    except keyword.DoesNotExist:
        return render(request, 'error_404.html')
    data_to_return = []
    all_pubs = []
    
    all_entries = keyword_publication.objects.filter(keyword_id = keywordID)   
    for entry in all_entries:
        pub_id = entry.publication_id
        p = publication.objects.get(id = pub_id)

        # find the publication's keywords
        pub_keywords = []
        all_pubs = keyword_publication.objects.filter(publication_id = pub_id)
        for pub in all_pubs:                            # loop through all publications's keywords ids
            pub_keyw_id = keyword.objects.get(id = pub.keyword_id)
            if pub_keyw_id.keyword not in pub_keywords:
                pub_keywords.append(pub_keyw_id.keyword)


        # find the publication's authors
        pub_co_authors = []
        all_co_authors = publication_co_author.objects.filter(publication_id = pub_id)
        for a in all_co_authors:
            co_author_entry = co_author.objects.get(id = a.co_author_id)
            co_author_name = co_author_entry.name.replace(",","")
            co_author_profile_url = co_author_entry.profile_url
            #co_author_affiliation = co_author_entry.affiliation
            pub_co_authors_dict = {}
            if co_author_name not in pub_co_authors:
                pub_co_authors_dict["name"] = co_author_name
                pub_co_authors_dict["profile_url"] = co_author_profile_url
                pub_co_authors.append(pub_co_authors_dict)

        # find the publication's inernal authors
        pub_authors = []
        all_int_authors = publication_author.objects.filter(publication_id = pub_id)
        for a in all_int_authors:
            author_entry = author.objects.get(id = a.author_id)
            author_name = author_entry.name.replace(",","")
            author_profile_url = "/authors/%s" % author_name.replace(" ","_")
            #co_author_affiliation = co_author_entry.affiliation
            pub_authors_dict = {}
            if author_name not in pub_co_authors:
                pub_authors_dict["name"] = author_name
                pub_authors_dict["profile_url"] = author_profile_url
                pub_co_authors.append(pub_authors_dict)

        publication_dict = {}
        publication_dict["title"] = p.pub_title
        publication_dict["url"] = p.pub_url
        publication_dict["venue"] = p.pub_venue
        publication_dict["date"] = p.pub_date
        publication_dict["type"] = p.pub_type
        publication_dict["doi"] = p.pub_doi
        publication_dict["citations"] = p.pub_citations
        publication_dict["keywords"] = pub_keywords
        publication_dict["co_authors"] = pub_co_authors
        ########################################################################################
        pubs_cited = publication_publication_cited.objects.filter(publication_id = pub_id)
        cited_doc = []
        all_cited_pub_ids = []
        for pub in pubs_cited:
            if pub.publication_cited_id not in all_cited_pub_ids:
                all_cited_pub_ids.append(pub.publication_cited_id)
                doc = publication_cited.objects.get(id = pub.publication_cited_id)
                cited_doc.append([doc.pub_title,doc.pub_url])
        publication_dict["publications_cited"] = cited_doc
        ########################################################################################
        data_to_return.append(publication_dict) 

    sorted_data = sorted(data_to_return, key=lambda k: k['date'],reverse=True) 
    return render(request, 'publications_search_results.html',{'results':sorted_data,'keyword':keyw.strip(),'top_keyw_search':True})

def author_publications_keyword(request,authorName,keyWord):

    author_name = authorName.replace("_"," ")
    keyw = keyWord.replace("_"," ")
    #keyw_new = "%{0}%",(keyw)
    # return HttpResponse(keyw)
    # k = keyword.objects.filter(keyword__contains=keyw)[:1].get()     #here we use .filter in case there are multiply results
    # if len(k) >=2:
    #      keywordID = k[0].id
    # else:
    # k = keyword.objects.filter(keyword__contains = keyw)[:1].get()
    k = keyword.objects.get(keyword = keyw)
    keywordID = k.id
    a = author.objects.get(name = author_name)
    authorID = a.id

    author_pubs = publication_author.objects.filter(author_id = authorID)   # all author's publications
    data_to_return = []
    all_pubs = []
    for pub in author_pubs:    
        p = publication.objects.get(id = pub.publication_id) 
        all_entries = keyword_publication.objects.filter(keyword_id = keywordID)   # all the keywords which used in this publication
        for entry in all_entries:
            
            if p.id == entry.publication_id and p.pub_title not in all_pubs:   

                # find the publication's keywords
                pub_keywords = []
                pubs_keyws = keyword_publication.objects.filter(publication_id = p.id)
                for pub_keyw in pubs_keyws:     # loop through all publications's keywords ids
                    pub_keyw_id = keyword.objects.get(id = pub_keyw.keyword_id)
                    if pub_keyw_id.keyword not in pub_keywords:
                        pub_keywords.append(pub_keyw_id.keyword)


                # find the publication's authors
                pub_co_authors = []
                all_co_authors = publication_co_author.objects.filter(publication_id = p.id)
                for a in all_co_authors:
                    co_author_entry = co_author.objects.get(id = a.co_author_id)
                    co_author_name = co_author_entry.name.replace(",","")
                    co_author_profile_url = co_author_entry.profile_url
                    #co_author_affiliation = co_author_entry.affiliation
                    pub_co_authors_dict = {}
                    if co_author_name not in pub_co_authors:
                        pub_co_authors_dict["name"] = co_author_name
                        pub_co_authors_dict["profile_url"] = co_author_profile_url
                        pub_co_authors.append(pub_co_authors_dict)

                # find the publication's inernal authors
                pub_authors = []
                all_int_authors = publication_author.objects.filter(publication_id = p.id)
                for a in all_int_authors:
                    author_entry = author.objects.get(id = a.author_id)
                    author_name = author_entry.name.replace(",","")
                    author_profile_url = "/authors/%s" % author_name.replace(" ","_")
                    #co_author_affiliation = co_author_entry.affiliation
                    pub_authors_dict = {}
                    if author_name not in pub_co_authors:
                        pub_authors_dict["name"] = author_name
                        pub_authors_dict["profile_url"] = author_profile_url
                        pub_co_authors.append(pub_authors_dict)


                publication_dict = {}
                publication_dict["title"] = p.pub_title
                all_pubs.append(p.pub_title)
                publication_dict["url"] = p.pub_url
                publication_dict["venue"] = p.pub_venue
                publication_dict["date"] = p.pub_date
                publication_dict["type"] = p.pub_type
                publication_dict["doi"] = p.pub_doi
                publication_dict["citations"] = p.pub_citations
                publication_dict["keywords"] = pub_keywords
                publication_dict["co_authors"] = pub_co_authors
                ########################################################################################
                pubs_cited = publication_publication_cited.objects.filter(publication_id = p.id)
                cited_doc = []
                all_cited_pub_ids = []
                for pub in pubs_cited:
                    if pub.publication_cited_id not in all_cited_pub_ids:
                        all_cited_pub_ids.append(pub.publication_cited_id)
                        doc = publication_cited.objects.get(id = pub.publication_cited_id)
                        cited_doc.append([doc.pub_title,doc.pub_url])
                publication_dict["publications_cited"] = cited_doc
                ########################################################################################
                data_to_return.append(publication_dict) 

    sorted_data = sorted(data_to_return, key=lambda k: k['date'],reverse=True) 
    return render(request, 'publications_search_results.html',{'results':sorted_data,'keyword':keyw.strip(),'author_name':author_name})

                

def author_profile(request,author_name):

    authorName = author_name.replace("_"," ")
    author_exist = author.objects.get(name = authorName)
    if author_exist:
        authorID = author_exist.id
        author_orcID = author_exist.orcID;
        author_url = author_exist.profile_url
        publications = []
        author_subject_areas = []

        all_entries = subject_area_author.objects.filter(author_id = authorID)
        for entry in all_entries:
            sub_area = subject_area.objects.get(id = entry.subject_area_id)
            author_subject_areas.append(sub_area.area)

        all_citations = []
        all_entries = publication_author.objects.filter(author_id = authorID)
        total_citations = 0

        co_authors = []
        co_authors_names = []
        all_authors = []

        for entry in all_entries:       # loop through all author's publications
            publication_dict = {}
            all_cited_pub_ids = []
            try:
                pub = publication.objects.get(id = entry.publication_id)
            except publication.DoesNotExist:
                continue
            if pub.pub_citations != "-":
                total_citations = total_citations + int(pub.pub_citations)
            pub_id = pub.id
            pub_title = pub.pub_title
            pub_doi = pub.pub_doi
            pub_url = pub.pub_url
            pub_venue = pub.pub_venue
            pub_date = pub.pub_date
            pub_type = pub.pub_type
            pub_citations = pub.pub_citations
            all_citations.append(pub_citations)

            # find the publication's keywords
            pub_keywords = []
            pubs_keyws = keyword_publication.objects.filter(publication_id = entry.publication_id)
            for pub_keyw in pubs_keyws:             # loop through all publications's keywords ids
                pub_keyw_id = keyword.objects.get(id = pub_keyw.keyword_id)
                if pub_keyw_id.keyword not in pub_keywords:
                    pub_keywords.append(pub_keyw_id.keyword)

            
            # find external co authors for each publication
            pub_co_authors = []
            all_co_authors = publication_co_author.objects.filter(publication_id = entry.publication_id)
            for a in all_co_authors:
                try:
                    co_author_entry = co_author.objects.get(id = a.co_author_id)
                    co_author_id = co_author_entry.id
                    co_author_name = co_author_entry.name.replace(",","")
                    co_author_profile_url = co_author_entry.profile_url
                except co_author.DoesNotExist:
                    continue
                
                try:
                    co_author_aff = co_author_affiliation.objects.filter(co_author_id = co_author_id)[:1].get() # in case of many results
                except co_author_affiliation.DoesNotExist:
                    continue
                co_author_aff_name = affiliation.objects.get(id = co_author_aff.affiliation_id).affiliation_name
                
                pub_co_authors_dict = {}
                if co_author_name not in pub_co_authors:
                    pub_co_authors_dict["name"] = co_author_name
                    pub_co_authors_dict["profile_url"] = co_author_profile_url
                    pub_co_authors.append(pub_co_authors_dict)

                co_author_dict = {}
                #if co_author_name not in all_authors:
                if not check_duplicates(co_author_name,all_authors,authorName):
                    all_authors.append(co_author_name)
                    co_author_dict["name"] = co_author_name
                    co_author_dict["weight"] = 0
                    co_author_dict["profile_url"] = co_author_profile_url
                    co_author_dict["affiliation"] = co_author_aff_name
                    co_authors.append(co_author_dict)
                co_authors_names.append(co_author_name)

            
            # find interior co authors for each publication      
            all_co_authors = publication_author.objects.filter(publication_id = entry.publication_id)
            for a in all_co_authors:
                try:
                    author_entry = author.objects.get(id = a.author_id)
                    author_id = author_entry.id
                    author_name = author_entry.name.replace(",","")
                    author_profile_url = "/authors/"+author_name.replace(" ","_")
                except co_author.DoesNotExist:
                    continue
                #####################################################################
                pub_co_authors_dict = {}
                if author_name not in pub_co_authors and author_name != authorName:
                    pub_co_authors_dict["name"] = author_name
                    pub_co_authors_dict["profile_url"] = author_profile_url
                    pub_co_authors.append(pub_co_authors_dict)
                co_author_dict = {}
                #####################################################################
                #if co_author_name not in all_authors:
                if not check_duplicates(author_name,all_authors,authorName):
                    all_authors.append(author_name)
                    co_author_dict["name"] = author_name
                    co_author_dict["weight"] = 0
                    co_author_dict["profile_url"] = author_profile_url
                    co_author_dict["affiliation"] = "Electrical and Computer Engineering,University of Thessaly"
                    co_authors.append(co_author_dict)
                co_authors_names.append(author_name)
            #########################################################################################

            publication_dict["title"] = pub_title
            publication_dict["url"] = pub_url
            if pub_venue != "-":
                publication_dict["venue"] = pub_venue
            publication_dict["date"] = pub_date
            publication_dict["type"] = pub_type
            publication_dict["doi"] = pub_doi
            publication_dict["citations"] = pub_citations
            publication_dict["keywords"] = pub_keywords
            publication_dict["co_authors"] = pub_co_authors
            ########################################################################################
            pubs_cited = publication_publication_cited.objects.filter(publication_id = pub_id)
            cited_doc = []
            
            for pub in pubs_cited:
                
                    doc = publication_cited.objects.get(id = pub.publication_cited_id)
                    if doc.pub_title not in all_cited_pub_ids:
                        all_cited_pub_ids.append(doc.pub_title)
                        cited_doc.append([doc.pub_title,doc.pub_url])
            publication_dict["publications_cited"] = cited_doc
            ########################################################################################
            publications.append(publication_dict)  
            pub_keywords = []      
        # end for loop     


        # calculate eaach co_autor's weight    
        for each_author in all_authors:
            for item in co_authors:
                if item["name"] == each_author:
                    item["weight"] = co_authors_names.count(each_author)

        keywords_to_returned = []
        publication_freq = {}

        # calculate the author's h-index
        h_index = 0
        sorted_citations = sorted(all_citations, key=int,reverse=True) 
        for i in range(1,len(sorted_citations)):
            if sorted_citations[i] < i:
                h_index = i-1
                break
            else:
                h_index = i

        # calculate the author's citation impact
        c = 0
        citations = 0
        citation_impact = 0
        all_publications = publication_author.objects.filter(author_id = authorID)
        for pub in all_publications:
            p = publication.objects.get(id = pub.publication_id)
            if p.pub_date != "-" and p.pub_date != "":
                if float(p.pub_date) >= 2000:
                    c = c + 1
                    citations = citations + p.pub_citations
        if c != 0:
            citation_impact = citations/c   

        sorted_by_date = sorted(publications, key=lambda k: k['date'],reverse=True)
       
        return render(request, 'author.html',{'author_name':authorName,'author_url':author_url,'h_index':h_index,'citation_impact':citation_impact,'author_subject_areas':author_subject_areas,'total_publications':len(all_entries),'total_citations':total_citations
            ,'co_authors':co_authors,'has_photo_profile':authorName.lower().replace(" ","_"),'author_publications':sorted_by_date,"orcID":author_orcID})
    else:   # show 404 template error
        return render(request,'error_404.html')

def about(request):

    return render(request,'about.html',{'department':True})

def about_2(request):       # CENTRAL PAGE EDITION
    
    return render(request,'about.html',{'department':False})

def access_db(request):
    if request.method == "GET":
        if request.GET['action'] == "access_db_publications":
            all_dates = []
            data_to_return = []
            min_date = 2000 # MUST BE DYNAMIC
            if request.GET['source'] == "index":
                all_entries = publication.objects.all()

                for entry in all_entries:
                    pub_date = entry.pub_date.strip()
                    if pub_date not in all_dates and pub_date != "-" and (int(pub_date) >= min_date):
                        all_dates.append(pub_date)      # collect all dates
                publication_freq = {}

                for date in all_dates:
                    entries = publication.objects.filter(pub_date = date)
                    freq = len(entries)
                    publication_freq['pub'] = (date,freq)
                    data_to_return.append(publication_freq)
                    publication_freq = {}
            else:       # author
                author_name = request.GET['author']
                authorID = author.objects.get(name = author_name.strip())
                all_entries = publication_author.objects.filter(author_id = authorID.id)
                publications_dict = {}
                for entry in all_entries:
                    pub = publication.objects.get(id = entry.publication_id)
                    if pub.pub_date not in all_dates and pub.pub_date != "-":
                        all_dates.append(pub.pub_date)
                        publications_dict[pub.pub_date] = 0


                #########################################################################
                for entry in all_entries:
                    pub = publication.objects.get(id = entry.publication_id)
                    pub_date = pub.pub_date
                    if pub_date in all_dates:
                        pub_citations = pub.pub_citations
                        publications_dict[pub_date]+=1

                # insert the  dicrionary's data into a data_to_return list 
                for year, freq in publications_dict.items():
                    return_data_dict = {}
                    
                    return_data_dict['pub'] = (year,freq)
                    data_to_return.append(return_data_dict)

                sorted_data = sorted(data_to_return, key=lambda k: k['pub']) 

                #########################################################################
                
            
           
            return HttpResponse(json.dumps(sorted_data), content_type='application/json')

        elif request.GET['action'] == "access_db_affiliations":
            
            not_rest_affs = ["Thessaly","thessaly","volos","Volos"]     # must be dynamic
            return HttpResponse(json.dumps(find_affiliations(not_rest_affs,"access_db")), content_type='application/json')

        elif request.GET['action'] == "access_db_affiliations_central_page":    # ONLY CENTRAL PAGE EDITION
            
            not_rest_affs = ["Thessaly","thessaly","volos","Volos"]     # must be dynamic
            #return HttpResponse(json.dumps(find_affiliations_central_page(not_rest_affs)), content_type='application/json')
            return HttpResponse(json.dumps(find_affiliations(not_rest_affs,"access_db")), content_type='application/json')

        elif request.GET['action'] == "access_db_marker_content_central_page":

            connection = MySQLdb.connect(host="localhost",user="root",passwd="",db="uth_research_central_db")
            connection.set_character_set('utf8')
            cur = connection.cursor()

            affiliation_id = request.GET['marker_id']
            affiliations = []
            affiliations_ids = []
            data_to_return = []
            not_rest_affs = ["Thessaly","thessaly","volos","Volos"]     # must be dynamic

            query = "SELECT * FROM app_affiliation WHERE id = %s"
            cur.execute(query,[affiliation_id])
            aff = cur.fetchall()
            
            affiliation_name = aff[0][1]
            
            
            query = "SELECT department_id FROM app_affiliation_department WHERE affiliation_id = %s"
            cur.execute(query,[int(affiliation_id)])
            aff_2 = cur.fetchall()

            if aff_2:
                query = "SELECT name FROM app_departments WHERE id = %s"
                cur.execute(query,[aff_2[0][0]])
                aff = cur.fetchall()

                affil = {}
                affil["aff_name"] = affiliation_name
                affil["coll_department"] = aff[0][0]
                    
                data_to_return.append(affil)

            return HttpResponse(json.dumps(data_to_return), content_type='application/json')
        
        elif request.GET['action'] == "access_db_marker_content":

            affiliation_id = request.GET['marker_id']
            affiliations = []
            affiliations_ids = []
            data_to_return = []
            not_rest_affs = ["Thessaly","thessaly","volos","Volos"]     # must be dynamic

            aff = affiliation.objects.get(id = affiliation_id)
            
            #affiliation_id = entry.id
            affiliation_name = aff.affiliation_name
            #affiliation_location = aff.affiliation_location
               
            # find the co authors of the currrnt affiliation
            all_co_authors = co_author_affiliation.objects.filter(affiliation_id = affiliation_id)   # many results

            co_authors_name = []
            out_co_authors = []
            
            for each_co_author in all_co_authors:
                co_authors_name_dict = {}
                co_author_entry = co_author.objects.get(id = each_co_author.co_author_id)
                co_author_id = co_author_entry.id
                co_author_name = co_author_entry.name
                if co_author_name not in co_authors_name:
                    co_authors_name.append(co_author_name)
                    co_author_profile_url = co_author_entry.profile_url
                    co_authors_name_dict["name"] = co_author_name
                    co_authors_name_dict["profile_url"] = co_author_profile_url
                    out_co_authors.append(co_authors_name_dict)
                

                #find all the publications which the authors are connected
                pubs_ids = []
                co_authors_pubs = publication_co_author.objects.filter(co_author_id = co_author_id)
                for co_author_pub in co_authors_pubs:
                    if co_author_pub.publication_id not in pubs_ids:
                        pubs_ids.append(co_author_pub.publication_id)


                #find all the collaborated authors
                entries_co_authors = co_author_author.objects.filter(co_author_id = co_author_id)
                dep_collaborated_authors = []   # the authors of our university
                pub_entry = {}
                pubs = []
                
                affil = {}
                all_pubs_titles = []
                for entry in entries_co_authors:
                    authorId = entry.author_id
                    a = author.objects.get(id = authorId)
                    if a.name not in dep_collaborated_authors:
                        dep_collaborated_authors.append(a.name)
                    else:
                        continue
                    
                    # find all the publications associated with this author
                    for pub_id in pubs_ids:
                        pub_entry = {}
                        try:
                            p = publication_author.objects.filter(publication_id = pub_id,author_id = authorId)[:1].get()
                            pub = publication.objects.get(id = pub_id)
                            if pub.pub_title not in all_pubs_titles:
                                all_pubs_titles.append(pub.pub_title)
                                pub_entry["title"] = pub.pub_title
                                pub_entry["url"] = pub.pub_url
                                pubs.append(pub_entry)
                            else:
                                continue
                        except publication_author.DoesNotExist:
                            continue
                affil["aff_name"] = affiliation_name
                affil["out_co_authors"] = out_co_authors
                affil["len_all_co_authors"] = len(all_co_authors)
                affil["dep_collaborated_authors"] = dep_collaborated_authors
                affil["publications"] = pubs
                data_to_return.append(affil)

            return HttpResponse(json.dumps(data_to_return), content_type='application/json')
        elif request.GET['action'] == "access_db_publications_doc_types_author_1":

            publications_type = []
            conferences = 0
            publications = 0
            journals = 0
            books = 0
            other = 0
            total = 0
            author_name = request.GET['author']
            authorID = author.objects.get(name = author_name.strip())
            
            all_entries = publication_author.objects.filter(author_id = authorID.id)

            types = []
            for entry in all_entries:
                pub = publication.objects.get(id = entry.publication_id)
                types.append( pub.pub_type)
                if pub.pub_type == "Conference":
                    conferences+=1
                elif pub.pub_type == "Journal":
                    journals+=1 
                elif pub.pub_type == "Book":
                    books+=1   
                elif pub.pub_type == "other":
                    other+=1   
               
                total +=1

            type_journal = []
            type_journal.append("Journals")
            data = int((journals*100)/total)
            type_journal.append(data)
            if data != 0:
                publications_type.append(type_journal)

            type_conference = []
            type_conference.append("Conferences")
            data = int((conferences*100)/total)
            type_conference.append(data)
            if data != 0:
                publications_type.append(type_conference)

            type_book = []
            type_book.append("Books")
            data = int((books*100)/total)
            type_book.append(data)
            if data != 0:
                publications_type.append(type_book)

            type_other = []
            type_other.append("Other")
            data = int((other*100)/total)
            type_other.append(data)
            if  data != 0:
                publications_type.append(type_other)

            
            # data_to_return = []
            # data_to_return.append(publications_type)
            return HttpResponse(json.dumps(publications_type), content_type='application/json')

        elif request.GET['action'] == "access_db_publications_doc_types_author_2":

            now = datetime.datetime.now()
            conferences = []
            journals = []
            books = []
            others = []
            all_data = []
            data_to_return = []
            author_name = request.GET['author']
            a = author.objects.get(name = author_name.strip())
            all_pubs = publication_author.objects.filter(author_id = a.id)
            all_entries = []
            all_dates = []

            conferences_dict = {}
            journals_dict = {}
            books_dict = {}
            other_dict = {}

            for pub in all_pubs:
                
                entry = publication.objects.get(id = pub.publication_id)
                all_entries.append(entry)

                if entry.pub_date != "-" and entry.pub_type != "-":
                    
                    conferences_dict[entry.pub_date] = 0
                
                    journals_dict[entry.pub_date] = 0
                
                    books_dict[entry.pub_date] = 0
               
                    other_dict[entry.pub_date] = 0
                 
            for entry in all_entries:
                if entry.pub_date != "-" and entry.pub_type != "-":
                    if entry.pub_type == "Conference":
                        conferences_dict[entry.pub_date]+=1
                    elif entry.pub_type == "Journal":
                        journals_dict[entry.pub_date]+=1
                    elif entry.pub_type == "Book":
                        books_dict[entry.pub_date]+=1
                    elif entry.pub_type == "other":
                        other_dict[entry.pub_date]+=1

            sorted_data = sorted(conferences_dict.items(), key=lambda x: (x[0]))
            data_to_return.append(sorted_data)
            sorted_data = sorted(journals_dict.items(), key=lambda x: (x[0]))
            data_to_return.append(sorted_data)
            sorted_data = sorted(books_dict.items(), key=lambda x: (x[0]))
            data_to_return.append(sorted_data)
            sorted_data = sorted(other_dict.items(), key=lambda x: (x[0]))
            data_to_return.append(sorted_data)

            return HttpResponse(json.dumps(data_to_return), content_type='application/json')
     
          
        elif request.GET['action'] == "access_db_publications_citations":
            data_to_return = []
            min_date = 2000
            if request.GET['source'] == 'author':    # author page
                author_name = request.GET['author']
                authorID = author.objects.get(name = author_name.strip())
                all_entries = publication_author.objects.filter(author_id = authorID.id)
                all_dates = []
                citations = 0
                publication_citations = {}

                # initialization of all dates 
                for entry in all_entries:
                    pub = publication.objects.get(id = entry.publication_id)
                    if pub.pub_date not in all_dates and pub.pub_date != "-" :
                        publication_citations[pub.pub_date] = 0     # initialize the frequency of this date to 0
                        all_dates.append(pub.pub_date)      # save all dates

                
                for entry in all_entries:
                    pub = publication.objects.get(id = entry.publication_id)
                    pub_date = pub.pub_date
                    if pub_date in all_dates:
                        pub_citations = pub.pub_citations
                        publication_citations[pub_date]+=pub_citations      # update the frequnecy 
                

                # insert the  dicrionary's data into a data_to_return list 
                for year, citations in publication_citations.items():
                    return_data_dict = {}
                    
                    return_data_dict['pub'] = (year,citations)
                    data_to_return.append(return_data_dict)
                sorted_data = sorted(data_to_return, key=lambda k: k['pub'])
                return HttpResponse(json.dumps(sorted_data), content_type='application/json') 

            elif request.GET['source'] == 'central':    # ONLY CENTRAL EDITION
                connection = MySQLdb.connect(host="localhost",user="root",passwd="",db="uth_research_central_db")
                connection.set_character_set('utf8')
                cur = connection.cursor()
                now = datetime.datetime.now()

                query = " SELECT min(pub_date) FROM app_publication WHERE pub_date != %s "
                cur.execute(query,["-"])
                row = cur.fetchall()
                minimum_date = row[0][0]

                citations = 0
                for year in range(int(minimum_date),int(now.year)+1):
                    publication_citations = {} 
                    all_entries = publication.objects.filter(pub_date = year)
                    for entry in all_entries:
                        citations = citations + entry.pub_citations
                    publication_citations['pub'] = (year,citations)
                    citations = 0
                    data_to_return.append(publication_citations)

                return HttpResponse(json.dumps(data_to_return), content_type='application/json') 
            elif request.GET['source'] == 'index':
                now = datetime.datetime.now()
                citations = 0
                for year in range(min_date,int(now.year)+1):
                    publication_citations = {} 
                    all_entries = publication.objects.filter(pub_date = year)
                    for entry in all_entries:
                        citations = citations + entry.pub_citations
                    publication_citations['pub'] = (year,citations)
                    citations = 0
                    data_to_return.append(publication_citations)

                return HttpResponse(json.dumps(data_to_return), content_type='application/json')      
            
      
        elif request.GET['action'] == "access_db_publications_doc_types_index":
            if request.GET['source'] == 'index':
                now = datetime.datetime.now()
                min_date = 2000
                conferences = []
                journals = []
                books = []
                others = []
                all_data = []
                
                for i in range(min_date,int(now.year)+1):

                    conf_dict = {}
                    jour_dict = {}
                    book_dict = {}
                    other_dict = {}
                    
                    all_entries = publication.objects.filter(pub_type = "Conference",pub_date=i).count()
                    conf_dict["conference"] = (i,all_entries)
                    conferences.append(conf_dict)

                    all_entries = publication.objects.filter(pub_type = "Journal",pub_date=i).count()
                    jour_dict["journal"] = (i,all_entries)
                    journals.append(jour_dict)

                    all_entries = publication.objects.filter(pub_type = "Book",pub_date=i).count()
                    book_dict["book"] = (i,all_entries)
                    books.append(book_dict)

                    all_entries = publication.objects.filter(pub_type = "other",pub_date=i).count()
                    other_dict["other"] = (i,all_entries)
                    others.append(other_dict)

                all_data.append(conferences)
                all_data.append(journals)
                all_data.append(books)
                all_data.append(others)

                return HttpResponse(json.dumps(all_data), content_type='application/json')

            elif request.GET['source'] == 'central':    # ONLY CENTRAL EDITION

                connection = MySQLdb.connect(host="localhost",user="root",passwd="",db="uth_research_central_db")
                connection.set_character_set('utf8')
                cur = connection.cursor()
                now = datetime.datetime.now()

                query = " SELECT min(pub_date) FROM app_publication WHERE pub_date != %s "
                cur.execute(query,["-"])
                row = cur.fetchall()
                minimum_date = row[0][0]

                conferences = []
                journals = []
                books = []
                others = []
                all_data = []
                
                for i in range(int(minimum_date),int(now.year)+1):

                    conf_dict = {}
                    jour_dict = {}
                    book_dict = {}
                    other_dict = {}
                    
                    all_entries = publication.objects.filter(pub_type = "Conference",pub_date=i).count()
                    conf_dict["conference"] = (i,all_entries)
                    conferences.append(conf_dict)

                    all_entries = publication.objects.filter(pub_type = "Journal",pub_date=i).count()
                    jour_dict["journal"] = (i,all_entries)
                    journals.append(jour_dict)

                    all_entries = publication.objects.filter(pub_type = "Book",pub_date=i).count()
                    book_dict["book"] = (i,all_entries)
                    books.append(book_dict)

                    all_entries = publication.objects.filter(pub_type = "other",pub_date=i).count()
                    other_dict["other"] = (i,all_entries)
                    others.append(other_dict)

                all_data.append(conferences)
                all_data.append(journals)
                all_data.append(books)
                all_data.append(others)

                return HttpResponse(json.dumps(all_data), content_type='application/json')
        elif request.GET['action'] =="access_db_author_network":

            pub_co_authors = []
            all_authors = author.objects.all()
            data_to_return = []
            all_ex_names = []
            for auth in all_authors:
                author_name = auth.name
                all_entries = publication_author.objects.filter(author_id = auth.id)    # all the author's publications
                for entry in all_entries:

                    all_co_authors = publication_author.objects.filter(publication_id = entry.publication_id)
                    for a in all_co_authors:
                        co_author_entry = author.objects.get(id = a.author_id)
                        co_author_id = co_author_entry.id
                        co_author_name = co_author_entry.name.replace(",","")
                        if co_author_name == author_name:
                            continue
                        #co_author_profile_url = co_author_entry.profile_url
                        en = {}
                        en["name"] = co_author_name
                        en["imports"] = [author_name]
                        data_to_return.append(en)
                        # en = {}
                        # en["name"] = author_name
                        # en["imports"] = [co_author_name]
                        # data_to_return.append(en)
                        

                    # all_ext_co_authors = publication_co_author.objects.filter(publication_id = entry.publication_id)
                    # for a in all_ext_co_authors:
                    #     co_author_entry = co_author.objects.get(id = a.co_author_id)
                    #     co_author_id = co_author_entry.id
                    #     co_author_name = co_author_entry.name.replace(",","")
                    #     if co_author_name == author_name:
                    #         continue
                    #     # if co_author_name not in all_ex_names:
                    #     #     all_ex_names.append(co_author_name)
                        
                    #     #co_author_profile_url = co_author_entry.profile_url
                    #     en = {}
                    #     en["name"] = co_author_name
                    #     en["imports"] = [author_name]
                    #     data_to_return.append(en)
                    #     # en = {}
                    #     # en["name"] = author_name
                    #     # en["imports"] = [co_author_name]
                    #     # data_to_return.append(en)
                      

           

            # d = [
            #     {"name": "Manuel_Jose", "imports": ["vivant", "designer", "artista", "empreendedor"]},
            #     {"name": "vivant", "imports": ["artista"]},
            #     {"name": "designer", "imports": []},
            #     {"name": "artista", "imports": []},
            #     {"name": "empreendedor", "imports": []}, 
            #     {"name": "test1", "imports": ["test2"]},
            #     {"name": "test2", "imports": ["test1"]}, 
            #     {"name": "asdasdasdas", "imports": ["test1"]}

            #     ]

            return HttpResponse(json.dumps(data_to_return), content_type='application/json')

        elif request.GET['action'] == "access_db_author_profile_co_authors":

            author_name = request.GET['author_name']

            authorID = author.objects.get(name = author_name.strip()).id
            author_url = ""
            publications = []
          
            all_entries = publication_author.objects.filter(author_id = authorID)
           
            co_authors = []
            co_authors_names = []
            all_authors = []
            data_to_return = []
           
            root = {}
            root['Nodes'] = []
            root['Links'] = []
            for entry in all_entries:       # loop through all author's publications
                publication_dict = {}

                pub = publication.objects.get(id = entry.publication_id)
             
                # find the co authors for each publication
                pub_co_authors = []
                all_co_authors = publication_co_author.objects.filter(publication_id = entry.publication_id)
                
                for a in all_co_authors:
                    try:
                        co_author_entry = co_author.objects.get(id = a.co_author_id)
                        co_author_id = co_author_entry.id
                        co_author_name = co_author_entry.name.replace(",","")
                        co_author_profile_url = co_author_entry.profile_url
                    except co_author.DoesNotExist:
                        continue
                    try:
                        co_author_aff = co_author_affiliation.objects.filter(co_author_id = co_author_id)[:1].get() # in case of many results
                    except co_author_affiliation.DoesNotExist:
                        continue
                    co_author_aff_name = affiliation.objects.get(id = co_author_aff.affiliation_id).affiliation_name
                    
                    co_author_dict = {}
                    if not check_duplicates(co_author_name,all_authors,author_name):
                        all_authors.append(co_author_name)
                        co_author_dict["Id"] = co_author_id
                        co_author_dict["Name"] = co_author_name
                        co_author_dict["Weight"] = 0
                        co_author_dict["Url"] = co_author_profile_url
                        #co_author_dict["affiliation"] = co_author_aff_name

                        co_authors.append(co_author_dict)
                        root["Nodes"].append(co_author_dict)

                        
                    co_authors_names.append(co_author_name) # save all co-author names
            
            #### author entry #######
            co_author_dict = {}
            co_author_dict["Id"] = authorID
            co_author_dict["Name"] = author_name
            co_author_dict["Weight"] = 0
            co_author_dict["Url"] = "wwww.google.com"
            root["Nodes"].append(co_author_dict)
            ###########################
            # calculate eaach co_autor's weight    
            for each_author in all_authors:
                for item in co_authors:
                    if item["Name"] == each_author:
                        item["Weight"] = co_authors_names.count(each_author)

            for each_author in all_authors:
                for item in co_authors:
                    entry = {}
                    entry["Source"] = authorID
                    entry["Target"]= item["Id"]
                    entry["Value"] = "0"
                    root["Links"].append(entry)

            data_to_return.append(root)

            return HttpResponse(json.dumps(root), content_type='application/json')
      
          
        elif  request.GET['action'] == "access_db_main_areas":

            data = []
            links = []
            all_sub_areas_list = []
            all_sub_areas = subject_area.objects.all()
            for sub_area in all_sub_areas:
                if sub_area.area.strip() not in all_sub_areas_list:
                    all_sub_areas_list.append(sub_area.area)
                    sub_area_id = sub_area.id
                    all_sub_araes_authors = subject_area_author.objects.filter(subject_area_id = sub_area_id)
                    for s in all_sub_araes_authors:
                        auth = author.objects.get(id = s.author_id)
                        author_name = auth.name
                        links.append((sub_area.area,author_name))

            name_to_node = {}
            root = {'name': '', 'children': []}
            for parent, child in links:
                parent_node = name_to_node.get(parent)
                if not parent_node:
                    name_to_node[parent] = parent_node = {'name': parent}
                    root['children'].append(parent_node)
                name_to_node[child] = child_node = {'name': child}
                parent_node.setdefault('children', []).append(child_node)

            data = json.dumps(root, indent=4)

            return HttpResponse(data, content_type='application/json')

        elif  request.GET['action'] == "access_db_total_countries":

            data_to_return = []
            l = ["Country","Collaborations"]
            data_to_return.append(l)
            total_countries = affiliation.objects.values_list("affiliation_country", flat=True).distinct()
            for country in total_countries:
                c = affiliation.objects.filter(affiliation_country = country).count()
                entry = [country,c]
                data_to_return.append(entry)

            return HttpResponse(json.dumps(data_to_return), content_type='application/json')

        elif  request.GET['action'] == "access_db_total_countries_central_page":       # ONLY CENTRAL EDITION

            connection = MySQLdb.connect(host="localhost",user="root",passwd="",db="uth_research_central_db")
            connection.set_character_set('utf8')
            cur = connection.cursor()
            
            data_to_return = []
            l = ["Country","Collaborations"]
            data_to_return.append(l)

            query = "SELECT DISTINCT(affiliation_country) AS affiliation_country FROM app_affiliation ORDER BY affiliation_country DESC"
            cur.execute(query)
            total_countries = cur.fetchall()
            
            for country in total_countries:
                query = "SELECT COUNT(*) FROM app_affiliation WHERE affiliation_country = %s"
                cur.execute(query,[country[0]])
                row = cur.fetchall()
                c = row[0][0]
                entry = [country[0],c]
                data_to_return.append(entry)

            return HttpResponse(json.dumps(data_to_return), content_type='application/json')
       
        elif request.GET['action'] == "access_db_publications_cited_by":

            author_name = request.GET['author']
            authorID = author.objects.get(name = author_name.strip())
            data_to_return = []
            all_ids = []
            all_titles = []
            all_entries = publication_author.objects.filter(author_id = authorID.id)    # all author's publications

            for entry in all_entries:
                all_docs = publication_publication_cited.objects.filter(publication_id = entry.publication_id)
                
                for doc in all_docs:
                    docs_dict = {}   
                    cited_by_doc = publication_cited.objects.get(id = doc.publication_cited_id)

                    if doc.publication_cited_id not in all_ids:

                        all_ids.append(doc.publication_cited_id)
                        docs_dict["pub"] = (cited_by_doc.pub_title,cited_by_doc.pub_url)
                        data_to_return.append(docs_dict)
                    else:
                        continue
            return HttpResponse(json.dumps(data_to_return), content_type='application/json')

        elif request.GET['action'] == "access_db_author_profile_keywords":

            author_name = request.GET['author']
            authorID = author.objects.get(name = author_name.strip())
            all_entries = publication_author.objects.filter(author_id = authorID.id)
            all_keywords = []
            author_keywords = []
            for entry in all_entries:       # loop through all author's publications
                all_keyws = keyword_publication.objects.filter(publication_id = entry.publication_id)
                for keyw in all_keyws:             # loop through all publications's keywords ids
                    keyw_id = keyword.objects.get(id = keyw.keyword_id)
                    all_keywords.append(keyw_id.keyword)
                    if keyw_id.keyword not in author_keywords:
                        author_keywords.append(keyw_id.keyword)

            keywords_to_returned = []
           

            for each_keyword in author_keywords:
                keyword_freq = {}
                freq = all_keywords.count(each_keyword)
                keyword_freq['keyw'] = each_keyword
                keyword_freq['size'] = freq
                keywords_to_returned.append(keyword_freq)

            sorted_by_keyw_size = sorted(keywords_to_returned, key=lambda k: k['size'],reverse=True)

            if len(keywords_to_returned) >= 100:
                sorted_by_keyw_size = sorted_by_keyw_size[:70]
                # return HttpResponse(len(sorted_by_keyw_size))
            return HttpResponse(json.dumps(sorted_by_keyw_size), content_type='application/json')  



    else:
        return HttpResponse("NOT OK")



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
        if difflib.SequenceMatcher(None, element, a).ratio() > 0.65:
            return True
    return False

