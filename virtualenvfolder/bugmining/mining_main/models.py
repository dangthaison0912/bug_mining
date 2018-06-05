from datetime import datetime

from django.db import models
from django.utils import timezone

class Bug(models.Model):
    bug_id = models.CharField(max_length=10)
    updated_date = models.DateTimeField(default=datetime.now, blank=True)
    #to String
    def __str__(self):
        return self.bug_id


class File(models.Model):
    file_path =models.CharField(max_length=200)
    bugs = models.ManyToManyField(Bug)
    added = models.IntegerField(default=0)
    deleted = models.IntegerField(default=0)
    #to String
    def __str__(self):
        return self.file_path
