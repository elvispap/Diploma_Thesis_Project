from django.db import models
from PIL import Image


class publication(models.Model):
    pub_title = models.CharField(max_length=500)
    pub_url = models.CharField(max_length=600)
    pub_venue = models.CharField(max_length=200)
    pub_date = models.CharField(db_index=True,max_length=100)
    pub_type = models.CharField(db_index=True,max_length=50)
    pub_citations = models.IntegerField(max_length=11)
    pub_doi = models.CharField(max_length=200)


    def __unicode__(self):
        return u'%s' % (self.pub_title)

class publication_cited(models.Model):
    pub_title = models.CharField(max_length=500)
    pub_url = models.CharField(max_length=600)

    def __unicode__(self):
        return u'%s' % (self.pub_title)

class department_logo(models.Model):
    logo_image = models.ImageField(upload_to="app/static/img/logo")

    def __unicode__(self):
        return u'%s' % (self.logo_image)

class department_name(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return u'%s' % (self.name)

class author(models.Model):
    name = models.CharField(max_length=50)
    profile_url = models.CharField(max_length=200,blank=True)
    orcID = models.CharField(max_length=100,blank=True)
    scopusID = models.CharField(max_length=100,blank=True)
    microsoftID = models.CharField(max_length=100,blank=True)
    ieee = models.CharField(max_length=100,blank=True)

    

    def __unicode__(self):
        return u'%s' % (self.name)

class image(models.Model):
    author = models.ForeignKey(author)
    image = models.ImageField(upload_to="app/static/img/photo_profile")    

class co_author(models.Model):
    name = models.CharField(max_length=50)
    profile_url = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s' % (self.name)

class affiliation(models.Model):
    affiliation_name = models.CharField(max_length=200)
    affiliation_location = models.CharField(max_length=200)
    affiliation_country = models.CharField(db_index=True,max_length=100)

    def __unicode__(self):
        return u'%s' % (self.affiliation_name)
    
class co_author_author(models.Model):
    author = models.ForeignKey(author,db_index=True)
    co_author = models.ForeignKey(co_author)

class co_author_affiliation(models.Model):
    affiliation = models.ForeignKey(affiliation)
    co_author = models.ForeignKey(co_author,db_index=True)

class gen_affiliation(models.Model):
    affiliation = models.CharField(max_length=200)
    #author = models.ManyToManyField(author)

class gen_affiliation_author(models.Model):
    gen_affiliation = models.ForeignKey(gen_affiliation)
    author = models.ForeignKey(author)

class keyword(models.Model):
    keyword = models.CharField(max_length=100)
    freq = models.IntegerField(max_length=11,db_index = True)
    
    def __unicode__(self):
        return u'%s' % (self.keyword)

class keyword_publication(models.Model):
    publication = models.ForeignKey(publication)
    keyword = models.ForeignKey(keyword,db_index = True)


class publication_publication_cited(models.Model):
    publication = models.ForeignKey(publication)
    publication_cited = models.ForeignKey(publication_cited)
    
class publication_author(models.Model):
    publication = models.ForeignKey(publication)
    author = models.ForeignKey(author)

class publication_co_author(models.Model):
    
    publication = models.ForeignKey(publication)
    co_author = models.ForeignKey(co_author)
    
class subject_area(models.Model):
    area = models.CharField(max_length=100)
    
    def __unicode__(self):
        return u'%s' % (self.area)

class subject_area_author(models.Model):
    author = models.ForeignKey(author)
    subject_area = models.ForeignKey(subject_area)





    