# Create your views here.
from django.http import HttpResponse
from registration.models import Team,Participant
from django.core import serializers
from django.views.decorators.cache import cache_page
import simplejson as json
@cache_page(60 * 5)
def get_teams(request):
    return_data =  serializers.serialize("json", Team.objects.all())
    return HttpResponse(return_data, content_type="application/json")

@cache_page(60 * 5)
def get_teams_people(request):
    data = []
    for team in Team.objects.all():
        participants = Participant.objects.filter(teams=team)
        std_name = []
        for participant in participants:
            std_name.append({'student_id':participant.id,'student_name':participant.name})
        data.append({'team_name':team.name,'team_id':team.id,'students':std_name})
        
    return_data = json.dumps(data)
    return HttpResponse(return_data, content_type="application/json")