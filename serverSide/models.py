from django.db import models
from django.urls import reverse
from datetime import datetime
from django.utils import timezone

class User(models.Model):
    name = models.CharField(max_length=100)
    login = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    lastUpdated = models.DateTimeField(auto_now=True)
    validity = models.BooleanField(default=True)

    def __str__(self):
        return self.login
    

class Directory(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    availability = models.BooleanField(default=True)
    parentDirectory = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    path = models.TextField(blank=True)
    level = models.CharField(blank=True, max_length=30)
    lastUpdated = models.DateTimeField(auto_now=True)
    validity = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class File(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    availability = models.BooleanField(default=True)
    ffile = models.FileField()
    directory = models.ForeignKey(Directory, related_name='files', on_delete=models.CASCADE)
    lastUpdated = models.DateTimeField(auto_now=True)
    validity = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class SectionCategory(models.Model):

    category = models.CharField(max_length=50)
    lastUpdated = models.DateTimeField(auto_now=True)
    validity = models.BooleanField(default=True)

    def __str__(self):
        return (str(self.pk) + self.category)

class StatusSection(models.Model):

    status = models.CharField(max_length=30)
    lastUpdated = models.DateTimeField(auto_now=True)
    validity = models.BooleanField(default=True)

class StatusData(models.Model):

    statusDataField = models.CharField(max_length=1000)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lastUpdated = models.DateTimeField(auto_now=True)
    validity = models.BooleanField(default=True)

class FileSection(models.Model):

    name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    category = models.OneToOneField(SectionCategory, on_delete=models.CASCADE)
    status = models.OneToOneField(StatusSection, on_delete=models.CASCADE, null=True, blank=True)
    statusData = models.OneToOneField(StatusData, on_delete=models.CASCADE, null=True, blank=True)
    parentFile = models.ForeignKey(File, related_name='sections', on_delete=models.CASCADE)
    parentSection = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    sectBegin = models.IntegerField(default=0)
    sectEnd = models.IntegerField(default=0)
    lastUpdated = models.DateTimeField(auto_now=True)
    validity = models.BooleanField(default=True)

    def __str__(self):
        return (str(self.pk) + " " + str(self.sectBegin) + " " + str(self.sectEnd))