# Create your views here.
from django.http import HttpResponse
from registration.models import Team
from django.core import serializers
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)
def get_teams(request):
    return_data =  serializers.serialize("json", Team.objects.all())
    return HttpResponse(return_data, content_type="application/json")