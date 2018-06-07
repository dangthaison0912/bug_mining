from django.contrib import admin

from .models import Bug, File, Author

admin.site.register(Bug)
admin.site.register(File)
admin.site.register(Author)
