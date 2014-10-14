from django.conf.urls import patterns, include, url
from uth_research import views
from django.contrib import admin
from django.conf.urls import handler404
from django.conf.urls import handler500
admin.autodiscover()

urlpatterns = patterns('',
   
    url(r'^$', views.central_page, name='home'),
    url(r'^home/$', views.central_page, name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^eece/', views.home),
    url(r'^search_by_keyword/$', views.home_search_by_keyword),
    url(r'^publications/$',views.publications),
    url(r'^all_publications/$',views.all_publications),
    url(r'^citations/$',views.citations),
    url(r'^all_citations/$',views.all_citations),
    url(r'^publications/keywords/([^/]+)$',views.publications_keyword),
    url(r'^publications/search/$',views.publications_search),
    url(r'^about/$',views.about),
    url(r'^about_2/$',views.about_2),
    url(r'^collaborations/$',views.collaborations),
    url(r'^authors/$',views.authors),
    url(r'^authors/([^/]+)/$',views.author_profile),
    url(r'^authors/([^/]+)/keywords/([^/]+)$',views.author_publications_keyword),
    url(r'^access_db/$', views.access_db),

    
    
)
handler404 = 'views.my_custom_404_view'
handler500 = 'views.my_custom_500_view'