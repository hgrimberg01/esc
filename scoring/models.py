"""
ESC Scoring App, 2014
The following competitions fit under the Standard Scoring scheme:
    AIAA, Archery; EcoHawks, Battery Powered Car; EWB, Water Finding;
    SEDS, Water Rocket; KU Robotics, Mindstorms; ASME, Trebuchet;
    ASME, Rube Goldberg; Concrete Canoe, Sailing;  USGBC, LEED DEsign
    
The following require custom scoring schemes:
    ASCE/Steel Bridge, Pasta Bridge; AEI, Skyscraper; SPE, Drilling;
    Sigma Gamma Tau, Egg Drop; AIChe, Chemical Car; JMS, Gravity Car;
    PESO, Weight Lifting; SHPE, Indoor Catapults
"""

from django.db import models
from django.db.models import Max
from django.db.models import Min
from registration.models import Team
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
# Create your models here.

class Event(models.Model):
    name = models.CharField(max_length=64)
    max_score = models.FloatField()
    min_score = models.FloatField()
    score_types = settings.GLOBAL_SETTINGS['SCORE_TYPES']
    event_score_type = models.CharField(choices=score_types, max_length=16)
    owners = models.ManyToManyField(Group)
    def __unicode__(self):
        return self.name

class Score(models.Model):
    event = models.ForeignKey(Event, help_text='Select an Event')
    team = models.ForeignKey(Team, help_text='Enter the Team ID')
    score = models.FloatField(help_text='Enter the teams score',default=0.01)
    disqualified = models.BooleanField(help_text='Check if the score is disqualified')
    normalized_score = models.FloatField(blank=True, null=True,editable=False)
    dateTimeStamp = models.DateTimeField(auto_now=True)
    def save(self, force_insert=False, force_update=False):
        max_possible = self.event.max_score
        min_possible = self.event.min_score
        
        if max_possible > min_possible:
            if self.score > max_possible or self.score < min_possible:
                raise ValidationError("Impossible Score")
           
            else:
                
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

"""
Pasta Bridge divides the weight of the material supported by the 
weight of the bridge, highest score wins
"""
class PastaBridgeScore(Score):
    score_quotient = models.FloatField()
    def save(self, force_insert=False, force_update=False):
        max_possible = self.event.max_score
        min_possible = self.event.min_score
        
        # find max score
        max_quotient_query = PastaBridgeScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Max('score_quotient'))
        if max_quotient_query['score_quotient__max'] == None:
            max_possible = self.score_quotient
        elif self.score_quotient > max_quotient_query['score_quotient__max']:
            max_possible = max_quotient_query['score_quotient__max']
        else:
            max_possible = max_quotient_query['score_quotient__max']
        
        # find min score
        min_quotient_query = PastaBridgeScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Min('score_quotient'))
        if min_quotient_query['score_quotient__min'] == None or min_quotient_query['score_quotient__min']:
            min_possible = 0.0
        elif min_quotient_query['score_quotient__min'] > self.score_quotient:
            min_possible = self.score_quotient
        else:
            min_possible = min_quotient_query['score_quotient__min']
        
        # apply score for team
        self.score = self.score_quotient
        
        # normalize
        dif_high_low = max_possible - min_possible
        dif_score_high = max_possible - self.score
        self.normalized_score = settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'] - round((dif_score_high / dif_high_low) * settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'], settings.GLOBAL_SETTINGS['DECIMAL_PLACES_TO_ROUND'])
        super(PastaBridgeScore, self).save(force_insert, force_update)        

"""
Skyscraper scores by the following formula:
score = (Your Height / Tallest Height) + (Your Weight / Greatest Weight) + (Min Tower Weight / Your Tower Weight)
"""
class SkyscraperScore(Score):
    tower_height = models.FloatField()
    tower_weight = models.FloatField()
    weight_supported = models.FloatField()
    def save(self, force_insert=False, force_update=False):
        max_possible = self.event.max_score
        min_possible = self.event.min_score
        
        max_height_query = SkyScraperScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Max('tower_height'))
        if max_height_query['tower_height__max'] == None:
            max_height = self.tower_height
        elif self.tower_height > max_height_query['tower_height__max']:
            max_height = self.tower_height
        else:
            max_height = max_height_query['tower_height__max']
        
        max_weight_query = SkyScraperScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Max('weight_supported'))
        if max_weight_query['weight_supported__max'] == None:
            max_weight = self.weight_supported
        elif self.weight_supported > max_weight_query['weight_supported']:
            max_weight = self.weight_supported
        else:
            max_weight = max_weight_query['weight_supported__max']
            
        min_weight_query = SkyScraperScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Min('tower_weight'))
        if min_weight_query['tower_weight__min'] == None or min_weight_query['tower_weight__min'] == max_weight:
            min_weight = self.tower_weight
        elif self.tower_weight < min_weight_query['tower_weight__min']:
            min_weight = self.tower_weight
        else:
            min_weight = min_weight_query['tower_weight__min']
        
        self.score = (self.tower_height / max_height) + (self.weight_supported / max_weight) + (min_weight / self.tower_weight)
        
        dif_high_low = max_possible - min_possible
        dif_score_high = max_possible - self.score
        self.normalized_score = settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'] - round((dif_score_high / dif_high_low) * settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'], settings.GLOBAL_SETTINGS['DECIMAL_PLACES_TO_ROUND'])
        super(SkyscraperScore, self).save(force_insert, force_update)


class EggDropScore(Score):
    egg_safety_possible_scores = ((1.0, 'Intact'), (0.5, 'Broken'))
    flight_time = models.FloatField()
    weight = models.FloatField()
    creative_score = models.FloatField()
    egg_safety = models.FloatField(choices=egg_safety_possible_scores)
    def save(self, force_insert=False, force_update=False):
        max_possible = self.event.max_score
        min_possible = self.event.min_score
               
        max_flight_time_query = EggDropScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Max('flight_time'))
        if max_flight_time_query['flight_time__max'] == None:
            max_flight_time = self.flight_time
        elif self.flight_time > max_flight_time_query['flight_time__max']:
            max_flight_time = self.flight_time
        else:
            max_flight_time = max_flight_time_query['flight_time__max']
      
        max_weight_query = EggDropScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Max('weight'))
        min_weight_query = EggDropScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Min('weight'))
        
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
       
        dif_high_low = max_possible - min_possible
        dif_score_high = max_possible - self.score
        self.normalized_score = settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'] - round((dif_score_high / dif_high_low) * settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'], settings.GLOBAL_SETTINGS['DECIMAL_PLACES_TO_ROUND'])
        super(EggDropScore, self).save(force_insert, force_update)   

        
class DrillingMudScore(Score):
    ingredients_documented = models.BooleanField()
    number_of_ingredients = models.IntegerField()
    price_documented = models.BooleanField()
    price_per_liter = models.FloatField()
    slide_time = models.FloatField()
    price_time = models.FloatField(editable=False)
    cuttings_left = models.IntegerField()
    group_poster = models.BooleanField()
    def save(self, force_insert=False, force_update=False): 
        
        base_score = 25.0
        ingredient_score = 0.0
        ingredient_price_score = 0.0
        ingredient_doc_score = 0.0
        poster_score = 0.0
        # Set flag to indicate ingredients are NOT documented
        if not self.ingredients_documented:
            ingredient_doc_score = 1.0
        # Set flag to indicate price is NOT documented    
        if not self.price_documented:
            ingredient_price_score = 1.0
        # If group HAS a poster, subtract 5 points.    
        if self.group_poster:
            poster_score = -5.0
        if self.number_of_ingredients < 3:
            ingredient_score = 4.0
        elif self.number_of_ingredients > 3:
            ingredient_score = (self.number_of_ingredients - 3) * 0.5      
        # Price * Time    
        time_price = self.price_per_liter * self.slide_time
        self.price_time = time_price
        
        rank = DrillingMudScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).count() - DrillingMudScore.objects.exclude(disqualified=True).filter(team__division=self.team.division, price_time__gt=time_price).count()
        if rank == 0 or rank == None:
            rank = 1.0
            
        rank_score = rank - 1.0

        final_score = 25 + ingredient_doc_score + ingredient_score + ingredient_price_score + rank_score + self.cuttings_left + poster_score
        self.score = final_score
        
        max_possible = self.event.max_score
        min_possible = self.event.min_score
        
        dif_high_low = min_possible - max_possible
        dif_score_low = min_possible - self.score
        self.normalized_score = round((dif_score_low / dif_high_low) * settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'], settings.GLOBAL_SETTINGS['DECIMAL_PLACES_TO_ROUND'])
        super(DrillingMudScore, self).save(force_insert, force_update)


"""
Chemical Car is based purely on times, ties are broken by lower weights
"""
class ChemicalCarScore(Score):
    time = models.FloatField(help_text='Time for car')
    weight = models.FloatField(help_text='Weight for car')
    def save(self, force_insert=False, force_update=False):
        # Highest rank is last place, last place is the number of entrants with scores
        max_possible = ChemicalCarScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).count()
        if max_possible == 0 or max_possible == None:
            max_possible = 1
        
        # Find the number of cars that have better times
        time_rank = ChemicalCarScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).count() - ChemicalCarScore.objects.exclude(disqualified=True).filter(team__division=self.team.division, time__gte=self.time).count()
        if time_rank == 0 or time_rank == None:
            time_rank = 0.0
        
        # Find the number of cars that have the same time, but better weights
        weight_rank = (ChemicalCarScore.objects.exclude(disqualified=True).filter(team__division=self.team.division, time=self.time).count() - ChemicalCarScore.objects.exclude(disqualified=True).filter(team__division=self.team.division, time=self.time, weight__gt=self.weight).count())
        if weight_rank == 0 or weight_rank == None:
            weight_weight = 0.0
        
        # Add 1 to make automated score reporting give a sensible rank, but keep ranking based on zero for normalization 
        final_rank = time_rank + weight_rank
        self.score = final_rank
        
        num_compet = max_possible
        self.normalized_score = round(((num_compet - final_rank + 1) / num_compet) * settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'], settings.GLOBAL_SETTINGS['DECIMAL_PLACES_TO_ROUND'])
        super(ChemicalCarScore, self).save(force_insert, force_update)

      
"""
Weight lifting applies the following formula:
(Score)=[(Predicted force)-(Experimental force)] * (number of gears)
Smaller scores are better
"""
class WeightLiftingScore(Score):
    team_score = models.FloatField()
    def save(self, force_insert=False, force_update=False):
        max_possible = self.event.max_score
        min_possible = self.event.min_score
        
        max_score_query = WeightLiftingScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Max('team_score'))
        if max_score_query['team_score__max'] == None:
            max_possible = self.team_score
        elif max_score_query['team_score__max'] < self.team_score:
            max_possible = self.team_score
        else:
            max_possible = max_score_query['team_score__max']
        
        min_score_query = WeightLiftingScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Min('team_score'))
        if min_score_query['team_score__min'] == None or min_score_query['team_score__min'] == self.team_score:
            min_possible = 0.0
        elif min_score_query['team_score__min'] > self.team_score:
            min_possible = self.team_score
        else:
            min_possible = min_score_query['team_score__min']
        
        self.score = team_score
        
        # Lower scores are normalized to highest
        dif_high_low = max_possible - min_possible
        dif_score_high = self.score - min_possible
        
        self.normalized_score = settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'] - round((dif_score_high / dif_high_low) * settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'], settings.GLOBAL_SETTINGS['DECIMAL_PLACES_TO_ROUND'])
        super(GravityCarScore, self).save(force_insert, force_update)

        
class GravityCarScore(Score):
    time = models.FloatField(help_text='Time for car')
    weight = models.FloatField(help_text='Weight for car')
    def save(self, force_insert=False, force_update=False):
       max_time_query = GravityCarScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Max('time'))
       min_time_query = GravityCarScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Min('time'))
       max_weight_query = GravityCarScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Max('weight'))
       min_weight_query = GravityCarScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Min('weight'))
       
       if(max_time_query['time__max'] == None):
           max_time = self.time
       elif(max_time_query['time__max'] < self.time):
           max_time = self.time
       else:
          max_time = max_time_query['time__max']
          
       if(min_time_query['time__min'] == None or min_time_query['time__min'] == max_time ):
           min_time = 0.0
       elif(min_time_query['time__min'] > self.time):
           min_time = self.time
       else:
          min_time = min_time_query['time__min']
          
       if(max_weight_query['weight__max'] == None):
           max_weight = self.weight
       elif(max_weight_query['weight__max'] < self.weight):
           max_weight = self.weight
       else:
          max_weight = max_weight_query['weight__max']
          
       if(min_weight_query['weight__min'] == None or min_weight_query['weight__min'] == max_weight ):
           min_weight = 0.0
       elif(min_weight_query['weight__min'] > self.weight):
           min_weight = self.time
       else:
          min_weight = min_weight_query['weight__min']  
                            
       a = 50.0 * (max_time - self.time) / (max_time - min_time)
       b = 50.0 * (max_weight - self.weight) / (max_weight - min_weight)
       print a+b
       print max_time
       print self.time
       self.score = a + b
       
       max_possible = self.event.max_score
       min_possible = self.event.min_score
       
       dif_high_low = max_possible - min_possible
       dif_score_high = max_possible - self.score
       
       self.normalized_score = settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'] - round((dif_score_high / dif_high_low) * settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'], settings.GLOBAL_SETTINGS['DECIMAL_PLACES_TO_ROUND'])
       super(GravityCarScore, self).save(force_insert, force_update)


"""
Indoor Catapults
"""
class IndoorCatapultsScore(Score):
    team_score = models.FloatField()
    def save(self, force_insert=False, force_update=False):
        max_possible = self.event.max_score
        min_possible = self.event.min_score
        
        # find max score
        max_score_query = IndoorCatapultsScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Max('team_score'))
        if max_score_query['team_score__max'] == None:
            max_possible = self.team_score
        elif self.team_score > max_score_query['team_score__max']:
            max_possible = max_score_query['team_score__max']
        else:
            max_possible = max_score_query['team_score__max']
        
        # find min score
        min_score_query = IndoorCatapultsScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Min('team_score'))
        if min_score_query['team_score__min'] == None or min_score_query['team_score__min']:
            min_possible = 0.0
        elif min_score_query['team_score__min'] > self.team_score:
            min_possible = self.team_score
        else:
            min_possible = min_score_query['team_score__min']
        
        # apply score for team
        self.score = self.team_score
        
        # normalize
        dif_high_low = max_possible - min_possible
        dif_score_high = max_possible - self.score
        self.normalized_score = settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'] - round((dif_score_high / dif_high_low) * settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'], settings.GLOBAL_SETTINGS['DECIMAL_PLACES_TO_ROUND'])
        super(IndoorCatapultsScore, self).save(force_insert, force_update) 


class PreRegistration(models.Model):
    teams = models.ForeignKey(Team)
    event = models.ForeignKey(Event)
    def __unicode__(self):
        return self.teams.name + ' for ' + self.event.name

"""
# No longer included
class VolcanoScore(Score):
    time = models.FloatField()
    distance = models.FloatField()
    def save(self, force_insert=False, force_update=False):
        
        max_time_query = VolcanoScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Max('time'))
        min_time_query = VolcanoScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Min('time'))
        max_distance_query = VolcanoScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Max('distance'))
        min_distance_query = VolcanoScore.objects.exclude(disqualified=True).filter(team__division=self.team.division).aggregate(Min('distance'))
        
        if max_time_query['time__max'] == None:
            max_time = self.time
        elif max_time_query['time__max'] < self.time:
            max_time = self.time
        else:
            max_time = max_time_query['time__max']
            
        if min_time_query['time__min'] == None or min_time_query['time__min'] == max_time :
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
            
        if min_distance_query['distance__min'] == None or min_distance_query['distance__min'] == max_distance :
            min_distance = 00.00
        elif min_distance_query['distance__min'] > self.distance:
            min_distance = self.distance
        else:
            min_distance = min_distance_query['distance__min']    
            
            
        A = 50.0 * (self.time - min_time) / (max_time - min_time)
        B = 50.0 * (self.distance - min_distance) / (max_distance - min_distance)
   
        max_possible = self.event.max_score
        min_possible = self.event.min_score
        
        self.score = A + B
        print(self.score)
        
        dif_high_low = max_possible - min_possible
        dif_score_high = max_possible - self.score
        self.normalized_score = settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'] - round((dif_score_high / dif_high_low) * settings.GLOBAL_SETTINGS['MAX_NORMAL_SCORE'], settings.GLOBAL_SETTINGS['DECIMAL_PLACES_TO_ROUND'])
        
        
        super(VolcanoScore, self).save(force_insert, force_update)
"""