from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from adminplus import AdminSitePlus
from scoring.views import get_team_scores
from django.shortcuts import render_to_response
from django.views.generic.simple import direct_to_template
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
admin.site = AdminSitePlus()
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'esc.views.home', name='home'),
    # url(r'^esc/', include('esc.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/scoring/getEventScore/(?P<event_id>\d+)/$','scoring.admin.AllScoresForSingleEventByDivision'),
     url(r'^api/getTeamScore/(?P<team_id>\d+)/$','scoring.views.get_team_scores'),   
    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
     url(r'^mobile/$',direct_to_template, {'template': '/home/hgrimberg/workspace/mobile/index.html'}),
     url(r'^$','scoring.views.index'),
     url(r'^call/initial/$','scoring.views.get_phone_intro'),
     url(r'^call/getScore/$','scoring.views.get_phone_score'),
     url(r'^sms/getScore/$','scoring.views.get_sms_score'),
) #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#urlpatterns += staticfiles_urlpatterns()
