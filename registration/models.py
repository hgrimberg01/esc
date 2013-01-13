from django.db import models
from django.contrib.localflavor.us.models import PhoneNumberField,USStateField
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

class School(models.Model):
    name = models.CharField(max_length=128)
    address_line_1 = models.CharField(max_length=128)
    address_line_2 = models.CharField(max_length=128,blank=True,null=True)
    city = models.CharField(max_length=128)
    school_types = (('HS','High School'),('MS','Middle School'),('ES','Elementary School'))
    state = USStateField()
    zipcode = models.IntegerField()
    school_type = models.CharField(choices=school_types,max_length=16)
    dateTimeStamp = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.name



class TeacherProfile(models.Model):
    telephone = PhoneNumberField()
    school = models.ForeignKey(School)
    user = models.OneToOneField(User)
    dateTimeStamp = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        
        return self.user.get_full_name()

class Team(models.Model):
    name = models.CharField(max_length=64)
    school_types = (('HS','High School'),('MS','Middle School'),('ES','Elementary School'),('OTH','Other'))
    division = models.CharField(choices=settings.GLOBAL_SETTINGS['SCHOOL_TYPES'],max_length=8)
    dateTimeStamp = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.name
    
class Participant(models.Model):
    name = models.CharField(max_length=64)
    school = models.ForeignKey(School)
    teacher = models.ForeignKey(TeacherProfile)
    teams = models.ManyToManyField(Team)
    dateTimeStamp = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name