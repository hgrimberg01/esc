from django.contrib import admin
from scoring.models import Event, Score, EggDropScore,VolcanoScore  
from django import forms
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Max
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
import simplejson as json
admin.site.register(Event)
admin.site.register(VolcanoScore)
        
class ScoreForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ScoreForm, self).__init__(*args, **kwargs)
        standard_events = Event.objects.filter(event_score_type='STD')
        event_widget = self.fields['event'].widget
        choices = []
        for element in standard_events:
            choices.append((element.id, element.name))
        event_widget.choices = choices
    def clean_score(self):
        print(self.cleaned_data['event'])
        selected_event = Event.objects.get(name=self.cleaned_data['event'])
        if(selected_event.max_score > selected_event.min_score):
            if self.cleaned_data['score'] < 0:
                raise forms.ValidationError("Score Cannot Be Negative")
            elif self.cleaned_data['score'] >selected_event.max_score:
                raise forms.ValidationError("Score Cannot Be Greater Than Best Possible Score")
            elif self.cleaned_data['score'] < selected_event.min_score:
                raise forms.ValidationError("Score Cannot Be Less Than Worst Possible Score")
            else:
                return self.cleaned_data['score']
        elif selected_event.max_score < selected_event.min_score:
            if self.cleaned_data['score'] < 0:
                raise forms.ValidationError("Score Cannot Be Negative")
            elif self.cleaned_data['score'] < selected_event.max_score:
                raise forms.ValidationError("Score Cannot Be Less Than Best Possible Score")
            elif self.cleaned_data['score'] > selected_event.min_score:
                raise forms.ValidationError("Score Cannot Be Greater Than Worst Possible Score")
            else:
                return self.cleaned_data['score']
       
        
class ScoreAdmin(admin.ModelAdmin):
    form = ScoreForm
    pass


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'score_report','total_scores','high_school_scores','middle_school_scores','elementary_school_scores','other_school_scores')

    #def show_link(self, obj):
    #    return '<a href="%s">Click here</a>' % obj.get_absolute_url()
    
    def score_report(self, obj):
        return '<a href="/admin/scoring/getEventScore/%s ">Click here</a>' % obj.pk 
    def total_scores(self,obj):
        return str(Score.objects.filter(event=obj).count())
    def high_school_scores(self,obj):
        return str(Score.objects.filter(event=obj).filter(team__division='HS').count())
    def middle_school_scores(self,obj):
        return str(Score.objects.filter(event=obj).filter(team__division='MS').count())
    def elementary_school_scores(self,obj):
        return str(Score.objects.filter(event=obj).filter(team__division='ES').count())
    def other_school_scores(self,obj):
        return str(Score.objects.filter(event=obj).filter(team__division='OTH').count())
    
    
    score_report.allow_tags = True

admin.site.unregister(Event)
admin.site.register(Event,EventAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(EggDropScore)

def TopTenPerEvent(request):
    all_events = Event.objects.all()
   
    my_values = []
    for event in all_events:
        event_scores = Score.objects.filter(event=event)
        top_five_scores = event_scores.order_by('-normalized_score')[:10]
        my_values.append({'event':event,'scores':top_five_scores})
        
    #event_winners = Event.objects.annotate(top_scores = Max('normalized_score')).order_by('-top_scores')[:5]
    #pubs = Publisher.objects.annotate(num_books=Count('book')).order_by('-num_books')[:5]
    
    return render_to_response(
        "admin/scoring/report.html",
        {'score_list' : my_values},
        RequestContext(request, {}),
    )
TopTenPerEvent = staff_member_required(TopTenPerEvent)

def AllScoresForEvent(request):
    all_events = Event.objects.all()
   
    my_values = []
    for event in all_events:
        event_scores = Score.objects.filter(event=event)
        top_five_scores = event_scores.order_by('-normalized_score')
        my_values.append({'event':event,'scores':top_five_scores})
        
    #event_winners = Event.objects.annotate(top_scores = Max('normalized_score')).order_by('-top_scores')[:5]
    #pubs = Publisher.objects.annotate(num_books=Count('book')).order_by('-num_books')[:5]
    
    return render_to_response(
        "admin/scoring/report.html",
        {'score_list' : my_values},
        RequestContext(request, {}),
    )
AllScoresForEvent = staff_member_required(AllScoresForEvent)


admin.site.register_view('somepath', AllScoresForEvent)

def AllScoresForEventByDivision(request):
    all_events = Event.objects.all()
    all_divisions =  settings.GLOBAL_SETTINGS['SCHOOL_TYPES']
    
    my_values = []
    for event in all_events:
        div_event = []
        for division in all_divisions:
            div_temp  = division[0]
            event_division_score = Score.objects.filter(event=event).filter(team__division__exact=div_temp)
            final_scores = event_division_score.order_by('-normalized_score')
            div_event.append({'division':division[1],'scores':final_scores})
        
        my_values.append({'event':event,'div_scores':div_event})
    print my_values
    return render_to_response(
        "admin/scoring/event_division_score.html",
        {'score_list' : my_values},
        RequestContext(request, {}),
    )
    #print my_values
    
AllScoresForEventByDivision = staff_member_required(AllScoresForEventByDivision)
admin.site.register_view('somepath2', AllScoresForEventByDivision)    
    
    
def RetabulateEggDropScores(request):
    egg_drop = EggDropScore.objects.all()
    print(egg_drop[0].save())
    #for egg_drop_score in egg_drop:
        
    return  HttpResponseRedirect('/admin/')
RetabulateEggDropScores = staff_member_required(RetabulateEggDropScores)
admin.site.register_view('retabEggdrop', RetabulateEggDropScores)   
    