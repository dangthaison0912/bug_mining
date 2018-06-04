import datetime

from django.db import models
from django.utils import timezone

class Bug(models.Model):
    bug_id = models.CharField(max_length=10)
    fixed_date = models.DateTimeField('date fixed')
    #to String
    def __str__(self):
        return self.bug_id


class File(models.Model):
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE)
    file_path =models.CharField(max_length=200)
    #to String
    def __str__(self):
        return self.file_path
