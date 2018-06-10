from django.contrib import admin

from .models import Bug, File, Author, Release

admin.site.register(Bug)
admin.site.register(File)
admin.site.register(Author)
admin.site.register(Release)
