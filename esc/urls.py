from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from adminplus import AdminSitePlus
from scoring.views import get_team_scores

admin.site = AdminSitePlus()
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'esc.views.home', name='home'),
    # url(r'^esc/', include('esc.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
     url(r'^api/getTeamScore/(?P<team_id>\d+)/$','scoring.views.get_team_scores'),   
    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
     url(r'^$',lambda request: HttpResponse(""))
 
)
