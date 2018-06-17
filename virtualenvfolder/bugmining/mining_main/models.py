from datetime import datetime

from django.db import models
from django.utils import timezone

class Bug(models.Model):
    bug_id = models.CharField(max_length=10)
    #to String
    def __str__(self):
        return self.bug_id

class Release(models.Model):
    release_number = models.CharField(max_length=200)
    #to String
    def __str__(self):
        return self.release_number

class File(models.Model):
    file_path =models.CharField(max_length=200)
    involved = models.IntegerField(default=0)
    total_changeset = models.IntegerField(default=0)
    bugs = models.ManyToManyField(Bug)
    release = models.ForeignKey(Release, on_delete=models.CASCADE)
    added = models.IntegerField(default=0)
    deleted = models.IntegerField(default=0)
    #to String
    def __str__(self):
        return self.file_path

class Author(models.Model):
    author_name = models.CharField(max_length=200)
    files = models.ManyToManyField(File)
    def __str__(self):
        return self.author_name
