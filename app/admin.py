from django.contrib import admin
from app.models import *

class InlineImage(admin.TabularInline):
    model = image

class AuthorAdmin(admin.ModelAdmin):
    inlines = [InlineImage]

admin.site.register(department_logo)
admin.site.register(department_name)
admin.site.register(author,AuthorAdmin)
admin.site.register(publication)
admin.site.register(publication_cited)
admin.site.register(co_author)
admin.site.register(affiliation)
admin.site.register(keyword)
admin.site.register(subject_area)
admin.site.register(co_author_author)
admin.site.register(co_author_affiliation)
admin.site.register(keyword_publication)
admin.site.register(publication_publication_cited)
admin.site.register(publication_author)
admin.site.register(publication_co_author)
admin.site.register(subject_area_author)


