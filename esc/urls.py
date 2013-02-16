from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from adminplus import AdminSitePlus
from django.views.generic.simple import direct_to_template

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
admin.site = AdminSitePlus()
admin.autodiscover()

urlpatterns = patterns('',

     url(r'^admin/scoring/getEventScore/(?P<event_id>\d+)/$', 'scoring.admin.AllScoresForSingleEventByDivision'),
     url(r'^api/getTeamScore/(?P<team_id>\d+)/$', 'scoring.views.get_team_scores'),
     url(r'^api/getTeams/$', 'registration.views.get_teams'),
     url(r'^api/getTeamsAndStudents/$', 'registration.views.get_teams_people'),
     url(r'^admin/', include(admin.site.urls)),
  
     url(r'^register/thanks/$', direct_to_template, {
        'template': 'register/thanks.html'}),
     url(r'^$', 'scoring.views.index'),
        url(r'^register/$', 'register.views.reg_usr'),
     url(r'^call/initial/$', 'scoring.views.get_phone_intro'),
     url(r'^call/getScore/$', 'scoring.views.get_phone_score'),
     url(r'^sms/getScore/$', 'scoring.views.get_sms_score'),
)
