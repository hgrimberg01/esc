# Create your views here.
from scoring.models import Score,Team
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import simplejson as json
from twilio.twiml import Response
from django_twilio.decorators import twilio_view
from twilio.twiml import Response
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_page
import re

@cache_page(60 * 1)
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


def index(request):
    reg_b = re.compile(r"(android|bb\\d+|meego).+mobile|avantgo|bada\\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino", re.I|re.M)
    reg_v = re.compile(r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\\-|your|zeto|zte\\-", re.I|re.M)
    request.mobile = False
    if request.META.has_key('HTTP_USER_AGENT'):
        user_agent = request.META['HTTP_USER_AGENT']
        b = reg_b.search(user_agent)
        v = reg_v.search(user_agent[0:4])
        if b or v:
            return HttpResponseRedirect("/mobile/")
        else:
            return HttpResponseRedirect("http://groups.ku.edu/~kuesc/expo")
@csrf_exempt
#@require_POST    
@twilio_view   
def get_phone_intro(request):
    r = Response()
    r.gather(action='/call/getScore/',method='GET').say('Welcome to the Kay You Engineering EXPO Scoring System. For score reports, please enter your team number and press pound.',voice='woman',language='en-gb')
    
    return r

@csrf_exempt
#@require_POST    
@twilio_view   
def get_phone_score(request):
    r = Response()
    team_id = request.GET['Digits']
    try:
        team = Team.objects.get(pk=team_id)
        scores = Score.objects.filter(team=team)
        r.say("Scores for team, "+team.name,voice='woman',language='en-gb')
        r.pause(length=2)
       
        for score in scores:
            r.say('For Event "'+score.event.name + '", You have ' + str(score.score) + ' points. ',voice='woman',language='en-gb')
            r.pause(length=1)
        
        r.say("Thank you for calling. Goodbye!",voice='woman',language='en-gb')
        r.hangup()
        
    except Team.DoesNotExist:    
        r.say("We're sorry, The team number entered does not exist.")
    return r


