# Create your views here.
from scoring.models import Score,Team
from django.conf import settings
from django.http import HttpResponse
import simplejson as json
def get_team_scores(request,team_id):
    
    try:
        team = Team.objects.get(pk=team_id)
        scores = Score.objects.filter(team=team)
        
        if settings.GLOBAL_SETTINGS['SCHOOL_TYPES'][0][0] == team.division :
            division = settings.GLOBAL_SETTINGS['SCHOOL_TYPES'][0][1]
        elif settings.GLOBAL_SETTINGS['SCHOOL_TYPES'][1][0] == team.division:
            division = settings.GLOBAL_SETTINGS['SCHOOL_TYPES'][1][1]
        elif settings.GLOBAL_SETTINGS['SCHOOL_TYPES'][2][0] == team.division:
            division = settings.GLOBAL_SETTINGS['SCHOOL_TYPES'][2][1]
        elif settings.GLOBAL_SETTINGS['SCHOOL_TYPES'][3][0] == team.division:
            division = settings.GLOBAL_SETTINGS['SCHOOL_TYPES'][3][1]
        ready_scores = []
        for score in scores:
            ready_scores.append({'event':score.event.name,'points':score.score})
        
        return_data = {'status':1,'team_name':team.name,'division':division,'scores':ready_scores}
        
    except Team.DoesNotExist:
        return_data = {'status':0}
        
    print return_data
    return HttpResponse(json.dumps(return_data), content_type="application/json")
