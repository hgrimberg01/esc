from django.db import models
from django.contrib.localflavor.us.models import PhoneNumberField,USStateField
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

class School(models.Model):
    name = models.CharField(max_length=128)
    address_line_1 = models.CharField(max_length=128,blank=True,null=True)
    address_line_2 = models.CharField(max_length=128,blank=True,null=True)
    city = models.CharField(max_length=128,blank=True,null=True)
    state = USStateField(blank=True,null=True)
    zipcode = models.IntegerField(blank=True,null=True)
    school_type = models.CharField(choices=settings.GLOBAL_SETTINGS['SCHOOL_TYPES'],max_length=16)
    dateTimeStamp = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.name



class Teacher(models.Model):
    telephone = PhoneNumberField()
    school = models.ForeignKey(School)
    dateTimeStamp = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        
        return self.user.get_full_name()

class Team(models.Model):
    name = models.CharField(max_length=64)
    division = models.CharField(choices=settings.GLOBAL_SETTINGS['SCHOOL_TYPES'],max_length=8)
    school = models.ForeignKey(School)
    dateTimeStamp = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.name
    
class Participant(models.Model):
    name = models.CharField(max_length=64)
    school = models.ForeignKey(School,blank=True,null=True)
    teacher = models.ForeignKey(Teacher, blank=True,null=True)
    teams = models.ManyToManyField(Team,blank=True,null=True)
    dateTimeStamp = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name