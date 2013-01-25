from django.db import models
from django.db.models import Max
from django.db.models import Min
from registration.models import Team
from django.conf import settings
from django.contrib.auth.models import User,Group
from django.core.exceptions import ValidationError
# Create your models here.

class Event(models.Model):
    name = models.CharField(max_length=64)
    max_score = models.FloatField()
    min_score = models.FloatField()
    score_types = (('STD', 'Standard'), ('EGD', 'Egg Drop'), ('VLN', 'Volcano'))
    event_score_type = models.CharField(choices=score_types, max_length=16)
    owners = models.ManyToManyField(Group)
    def __unicode__(self):
        return self.name
    



class Score(models.Model):
    event = models.ForeignKey(Event)
    team = models.ForeignKey(Team)
    score = models.FloatField()
    normalized_score = models.FloatField(blank=True, null=True)
    dateTimeStamp = models.DateTimeField(auto_now=True)
    def save(self, force_insert=False, force_update=False):
        max_possible = self.event.max_score
        min_possible = self.event.min_score
    
        if max_possible > min_possible:
            if self.score > max_possible or self.score < min_possible:
                raise ValidationError("Impossible Score")
                print('invalid')
            else:
                print('valid')
                dif_high_low = max_possible - min_possible
                dif_score_high = max_possible - self.score
                self.normalized_score = settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'] - round((dif_score_high / dif_high_low) * settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'], settings.GLOBAL_SETTINGS['DECIMAL_PLACES_TO_ROUND'])
        elif min_possible > max_possible:     
            if self.score < max_possible or self.score > min_possible:
                raise ValidationError("Impossible Score")
            else:
                dif_high_low = min_possible - max_possible
                dif_score_low = min_possible - self.score
                self.normalized_score = round((dif_score_low / dif_high_low) * settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'], settings.GLOBAL_SETTINGS['DECIMAL_PLACES_TO_ROUND'])
        super(Score, self).save(force_insert, force_update)
  
    def __unicode__(self):
            return self.event.name + " for " + self.team.name + " @ " + str(self.dateTimeStamp) 
 
class EggDropScore(Score):
    egg_safety_possible_scores = ((1.0, 'Intact'), (0.5, 'Broken'))
    flight_time = models.FloatField()
    weight = models.FloatField()
    creative_score = models.FloatField()
    egg_safety = models.FloatField(choices=egg_safety_possible_scores)
    def save(self, force_insert=False, force_update=False):
        max_possible = self.event.max_score
        min_possible = self.event.min_score
       
        
        max_flight_time_query = EggDropScore.objects.filter(team__division=self.team.division).aggregate(Max('flight_time'))
        if max_flight_time_query['flight_time__max'] == None:
            max_flight_time = self.flight_time
        elif self.flight_time > max_flight_time_query['flight_time__max']:
            max_flight_time = self.flight_time
        else:
            max_flight_time = max_flight_time_query['flight_time__max']
      
        max_weight_query = EggDropScore.objects.filter(team__division=self.team.division).aggregate(Max('weight'))
        min_weight_query = EggDropScore.objects.filter(team__division=self.team.division).aggregate(Min('weight'))
        
        if max_weight_query['weight__max'] == None:
            max_weight = self.weight
        elif max_weight_query['weight__max'] < self.weight:
            max_weight = self.weight
        else:
            max_weight = max_weight_query['weight__max']
            
        if min_weight_query['weight__min'] == None or min_weight_query['weight__min'] == max_weight:
            min_weight = 0.0
        elif min_weight_query['weight__min'] > self.weight:
            min_weight = self.weight
        else:
            min_weight = min_weight_query['weight__min']
        
        flight_time_score = self.flight_time / max_flight_time
            
        weight_score = (max_weight - self.weight) / (max_weight - min_weight)
        self.score = self.egg_safety * (flight_time_score + weight_score + (self.creative_score / 10.0))
        print("Weight Score:"+str(weight_score))
        print("Flight Score:"+str(flight_time_score))
        print(self.score)
        dif_high_low = max_possible - min_possible
        dif_score_high = max_possible - self.score
        self.normalized_score = settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'] - round((dif_score_high / dif_high_low) * settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'], settings.GLOBAL_SETTINGS['DECIMAL_PLACES_TO_ROUND'])
        super(EggDropScore, self).save(force_insert, force_update)   


class VolcanoScore(Score):
    time = models.FloatField()
    distance = models.FloatField()
    def save(self, force_insert=False, force_update=False):
        
        max_time_query = VolcanoScore.objects.filter(team__division=self.team.division).aggregate(Max('time'))
        min_time_query = VolcanoScore.objects.filter(team__division=self.team.division).aggregate(Min('time'))
        max_distance_query = VolcanoScore.objects.filter(team__division=self.team.division).aggregate(Max('distance'))
        min_distance_query = VolcanoScore.objects.filter(team__division=self.team.division).aggregate(Min('distance'))
        
        if max_time_query['time__max'] == None:
            max_time = self.time
        elif max_time_query['time__max'] < self.time:
            max_time = self.time
        else:
            max_time = max_time_query['time__max']
            
        if min_time_query['time__min'] == None:
            min_time = 00.00
        elif min_time_query['time__min'] > self.time:
            min_time = self.time
        else:
            min_time = min_time_query['time__min']
            
        if max_distance_query['distance__max'] == None:
            max_distance = self.distance
        elif max_distance_query['distance__max'] < self.distance:
            max_distance = self.distance
        else:
            max_distance = max_distance_query['distance__max']
            
        if min_distance_query['distance__min'] == None:
            min_distance = 00.00
        elif min_distance_query['distance__min'] > self.distance:
            min_distance = self.distance
        else:
            min_distance = min_distance_query['distance__min']    
            
            
        A = 50.0*(self.time-min_time) / (max_time-min_time)
        B = 50.0*(self.distance-min_distance)/(max_distance-min_distance)
   
        max_possible = self.event.max_score
        min_possible = self.event.min_score
        
        self.score = A+B
        print(self.score)
        
        dif_high_low = max_possible - min_possible
        dif_score_high = max_possible - self.score
        self.normalized_score = settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'] - round((dif_score_high / dif_high_low) * settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'], settings.GLOBAL_SETTINGS['DECIMAL_PLACES_TO_ROUND'])
        
        super(VolcanoScore, self).save(force_insert, force_update)
