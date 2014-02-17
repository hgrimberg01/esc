from django.contrib import admin
from scoring.models import Event, Score, EggDropScore, PreRegistration, DrillingMudScore, GravityCarScore, SkyscraperScore, PastaBridgeScore, ChemicalCarScore, WeightLiftingScore, IndoorCatapultsScore
from registration.models import Team
from django import forms
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Max
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User, Group
import simplejson as json
from django.core.mail import send_mass_mail, EmailMultiAlternatives
from django.views.decorators.cache import cache_page

class PreRegistrationAdmin(admin.ModelAdmin):
    list_display = ('teams', 'event',)
    list_filter = ('event',)
    search_fields = ('teams__name', 'event__name',)
    raw_id_fields = ('teams',)
admin.site.register(PreRegistration, PreRegistrationAdmin)


class ScoreForm(forms.ModelForm):
    db_field = Score._meta.get_field_by_name('team')[0]

    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        widget=ForeignKeyRawIdWidget(db_field.rel, admin.site),
        required=True
    )
    def __init__(self, *args, **kwargs):

        super(ScoreForm, self).__init__(*args, **kwargs)
        standard_events = Event.objects.filter(event_score_type='STD').distinct()

        standard_events = standard_events.filter(owners__in=self.current_groups)
        # print standard_events
        event_widget = self.fields['event'].widget

        choices = []
        for element in standard_events:
            choices.append((element.id, element.name))
        event_widget.choices = choices

    def clean_team(self):
        selected_event = Event.objects.get(name=self.cleaned_data['event'])
        owners = selected_event.owners.all()

        try:
            team = self.cleaned_data['team']
        except:
             raise forms.ValidationError("Team ID is incorrect or does not exist")
        try:
            event_prereg = PreRegistration.objects.get(event=selected_event, teams=self.cleaned_data['team'])
        except:
            users = User.objects.filter(groups__in=owners)

            emails = [user.email for user in users]
            subject = 'ERROR:Team %s (Number: %s) is not registered for event %s' % (team.name, str(team.id), selected_event.name,)
            message = 'An error has occurred. \r\n  Team %s (Number: %s) is not registered for event %s. \n User:%s' % (team.name, str(team.id), selected_event.name, self.current_user.username,)
            html = '<!DOCTYPE html><html><head><title>%s</title>' % (subject,)
            html = html + '</head><body><h1>An Error Has Occurred</h1><br/><p>An error has occurred. </br><strong>  Team %s (Number: %s)</strong> is not registered for event<strong> %s </strong>.</p> </br><p>User:<strong> %s </strong> </p></body></html>' % (team.name, str(team.id), selected_event.name, self.current_user.username)
            email = EmailMultiAlternatives(subject=subject, body=message,
            bcc=emails,
            headers={'Reply-To': 'hgrimberg01@gmail.com', 'X-Mailer':'ESC EXPO System v1.0'})
            email.attach_alternative(html, "text/html")
            email.send()
            raise forms.ValidationError("Team is not registered for this event")
        return self.cleaned_data['team']

    def clean_score(self):
        selected_event = Event.objects.get(name=self.cleaned_data['event'])


        if(selected_event.max_score > selected_event.min_score):
            if self.cleaned_data['score'] < 0:
                raise forms.ValidationError("Score Cannot Be Negative")
            elif self.cleaned_data['score'] > selected_event.max_score:
                raise forms.ValidationError("Score Cannot Be Greater Than Best Possible Score of " + str(selected_event.max_score))
            elif self.cleaned_data['score'] < selected_event.min_score:
                raise forms.ValidationError("Score Cannot Be Less Than Worst Possible Score of " + str(selected_event.min_score))
            else:
                return self.cleaned_data['score']
        elif selected_event.max_score < selected_event.min_score:
            if self.cleaned_data['score'] < 0:
                raise forms.ValidationError("Score Cannot Be Negative")
            elif self.cleaned_data['score'] < selected_event.max_score:
                raise forms.ValidationError("Score Cannot Be Less Than Best Possible Score of " + str(selected_event.max_score))
            elif self.cleaned_data['score'] > selected_event.min_score:
                raise forms.ValidationError("Score Cannot Be Greater Than Worst Possible Score of " + str(selected_event.min_score))
            else:
                return self.cleaned_data['score']
        class Meta:
            model = Score


class ScoreAdmin(admin.ModelAdmin):
    form = ScoreForm
    list_display = ('event', 'team', 'score')
    list_filter = ('event', 'team__division')
    search_fields = ('team',)

    raw_id_fields = ('team',)
    def queryset(self, request):
        qs = super(ScoreAdmin, self).queryset(request)
        user_groups = request.user.groups.all()
        if request.user.is_superuser:
            return qs
        return qs.filter(event__owners__in=user_groups)

    def get_form(self, request, obj=None, **kwargs):
        form = super(ScoreAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        form.current_groups = request.user.groups.all()

        return form

    pass


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'score_report', 'total_scores', 'high_school_scores', 'middle_school_scores', 'elementary_school_scores', 'other_school_scores')
    search_fields = ('name',)

    # def show_link(self, obj):
    #    return '<a href="%s">Click here</a>' % obj.get_absolute_url()

    def score_report(self, obj):
        return '<a href="/admin/scoring/getEventScore/%s ">Click here</a>' % obj.pk
    def total_scores(self, obj):
        return str(Score.objects.filter(event=obj).count())
    def high_school_scores(self, obj):
        return str(Score.objects.filter(event=obj).filter(team__division='HS').count())
    def middle_school_scores(self, obj):
        return str(Score.objects.filter(event=obj).filter(team__division='MS').count())
    def elementary_school_scores(self, obj):
        return str(Score.objects.filter(event=obj).filter(team__division='ES').count())
    def other_school_scores(self, obj):
        return str(Score.objects.filter(event=obj).filter(team__division='OTH').count())

    def queryset(self, request):
        qs = super(EventAdmin, self).queryset(request)
        user_groups = request.user.groups.all()
        if request.user.is_superuser:
            return qs
        return qs.filter(owners__in=user_groups)


    score_report.allow_tags = True


admin.site.register(Event, EventAdmin)
admin.site.register(Score, ScoreAdmin)


def TopTenPerEvent(request):
    all_events = Event.objects.all()

    my_values = []
    for event in all_events:
        event_scores = Score.objects.filter(event=event)
        top_five_scores = event_scores.order_by('-normalized_score')[:10]
        my_values.append({'event':event, 'scores':top_five_scores})

    # event_winners = Event.objects.annotate(top_scores = Max('normalized_score')).order_by('-top_scores')[:5]
    # pubs = Publisher.objects.annotate(num_books=Count('book')).order_by('-num_books')[:5]

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
        my_values.append({'event':event, 'scores':top_five_scores})

    # event_winners = Event.objects.annotate(top_scores = Max('normalized_score')).order_by('-top_scores')[:5]
    # pubs = Publisher.objects.annotate(num_books=Count('book')).order_by('-num_books')[:5]

    return render_to_response(
        "admin/scoring/report.html",
        {'score_list' : my_values},
        RequestContext(request, {}),
    )
AllScoresForEvent = staff_member_required(AllScoresForEvent)


admin.site.register_view('AllEventScores', AllScoresForEvent)

def AllScoresForEventByDivision(request):
    all_events = Event.objects.all()
    all_divisions = settings.GLOBAL_SETTINGS['SCHOOL_TYPES']

    my_values = []
    for event in all_events:
        div_event = []
        for division in all_divisions:
            div_temp = division[0]
            event_division_score = Score.objects.exclude(disqualified=True).filter(event=event).filter(team__division__exact=div_temp)
            final_scores = event_division_score.order_by('-normalized_score')
            div_event.append({'division':division[1], 'scores':final_scores})

        my_values.append({'event':event, 'div_scores':div_event})
    print my_values
    return render_to_response(
        "admin/scoring/event_division_score.html",
        {'score_list' : my_values},
        RequestContext(request, {}),
    )
    # print my_values

AllScoresForEventByDivision = staff_member_required(AllScoresForEventByDivision)
admin.site.register_view('AllScoresForEventsByDivision', AllScoresForEventByDivision)

@cache_page(60 * 2)
def AllScoresForSingleEventByDivision(request, event_id):
    event = Event.objects.get(id=event_id)
    all_divisions = settings.GLOBAL_SETTINGS['SCHOOL_TYPES']
    div_event = []
    for division in all_divisions:
        div_temp = division[0]
        event_division_score = Score.objects.filter(event=event).filter(team__division__exact=div_temp)
        final_scores = event_division_score.order_by('-normalized_score')
        div_event.append({'division':division[1], 'scores':final_scores})

    print div_event


    return render_to_response(
        "admin/scoring/event_score.html",
        {'score_list' : div_event, 'event_title':event.name},
        RequestContext(request, {}),
    )
    # print my_values

AllScoresForSingleEventByDivision = staff_member_required(AllScoresForSingleEventByDivision)

# Drilling mud
def RetabulateDrillingMudScores(request):
    drilling_mud_scores = DrillingMudScore.objects.all()

    for drilling_mud_scores in drilling_mud_scores:
        drilling_mud_scores.save()
    return  HttpResponseRedirect('/admin/')
RetabulateDrillingMudScores = staff_member_required(RetabulateDrillingMudScores)
admin.site.register_view('retabDrillingMudScores','Tabulate Final Drilling Mud Scores',  view= RetabulateDrillingMudScores)

class DrillingMudForm(ScoreForm):
    def __init__(self, *args, **kwargs):

        super(DrillingMudForm, self).__init__(*args, **kwargs)
        standard_events = Event.objects.filter(event_score_type='DMUD').distinct()

        standard_events = standard_events.filter(owners__in=self.current_groups)

        event_widget = self.fields['event'].widget

        choices = []
        for element in standard_events:
            choices.append((element.id, element.name))
        event_widget.choices = choices


class DrillingMudAdmin(ScoreAdmin):
    form = DrillingMudForm
    def get_form(self, request, obj=None, **kwargs):
        form = super(DrillingMudAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        form.current_groups = request.user.groups.all()

        return form
    pass

# Gravity Car
def RetabulateGravityCarScores(request):
    gravity_car_scores = GravityCarScore.objects.all()

    for gravity_car_scores in gravity_car_scores:
        gravity_car_scores.save()
    return  HttpResponseRedirect('/admin/')
RetabulateGravityCarScores = staff_member_required(RetabulateGravityCarScores)
admin.site.register_view('retabGravityCarScores','Tabulate Final Gravity Car Scores', view=RetabulateGravityCarScores)

class GravityCarScoreForm(ScoreForm):
    def __init__(self, *args, **kwargs):

        super(GravityCarScoreForm, self).__init__(*args, **kwargs)
        standard_events = Event.objects.filter(event_score_type='GCAR').distinct()

        standard_events = standard_events.filter(owners__in=self.current_groups)

        event_widget = self.fields['event'].widget

        choices = []
        for element in standard_events:
            choices.append((element.id, element.name))
        event_widget.choices = choices

class GravityCarScoreAdmin(ScoreAdmin):
    form = GravityCarScoreForm
    def get_form(self, request, obj=None, **kwargs):
        form = super(GravityCarScoreAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        form.current_groups = request.user.groups.all()

        return form
    pass


# Egg drop
def RetabulateEggDropScores(request):
    egg_drop_scores = EggDropScore.objects.all()

    for egg_drop_score in egg_drop_scores:
        egg_drop_score.save()
    return  HttpResponseRedirect('/admin/')
RetabulateEggDropScores = staff_member_required(RetabulateEggDropScores)
admin.site.register_view('retabEggdrop','Tabulate Final Egg Drop Scores', view=RetabulateEggDropScores)

class EggDropScoreForm(ScoreForm):
    def __init__(self, *args, **kwargs):

        super(EggDropScoreForm, self).__init__(*args, **kwargs)
        standard_events = Event.objects.filter(event_score_type='EGD').distinct()

        standard_events = standard_events.filter(owners__in=self.current_groups)

        event_widget = self.fields['event'].widget

        choices = []
        for element in standard_events:
            choices.append((element.id, element.name))
        event_widget.choices = choices

class EggDropScoreAdmin(ScoreAdmin):
    form = EggDropScoreForm
    def get_form(self, request, obj=None, **kwargs):
        form = super(EggDropScoreAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        form.current_groups = request.user.groups.all()

        return form
    pass


# Skyscraper
def RetabulateSkyscraperScores(request):
    skyscraper_scores = SkyscraperScore.objects.all()
    
    for skycsraper_score in skyscraper_scores:
        skyscraper_score.save()
    return HttpResponseRedirect('/admin/')
RetabulateSkyscraperScores = staff_member_required(RetabulateSkyscraperScores)
admin.site.register_view('retabSkyscraper', 'Tabulate Final Skyscraper Scores', view=RetabulateSkyscraperScores)

class SkyscraperScoreForm(ScoreForm):
    def __init__(self, *args, **kwargs):

        super(SkyscraperScoreForm, self).__init__(*args, **kwargs)
        standard_events = Event.objects.filter(event_score_type='SKY').distinct()

        standard_events = standard_events.filter(owners__in=self.current_groups)

        event_widget = self.fields['event'].widget

        choices = []
        for element in standard_events:
            choices.append((element.id, element.name))
        event_widget.choices = choices

class SkyscraperScoreAdmin(ScoreAdmin):
    form = SkyscraperScoreForm
    def get_form(self, request, obj=None, **kwargs):
        form = super(SkyscraperScoreAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        form.current_groups = request.user.groups.all()

        return form
    pass

# Pasta bridge
def RetabulatePastaBridgeScores(request):
    pasta_bridge_scores = PastaBridgeScore.objects.all()
    
    for pasta_bridge_score in pasta_bridge_scores:
        pasta_bridge_score.save()
    return HttpResponseRedirect('/admin/')
RetabulatePastaBridgeScores = staff_member_required(RetabulatePastaBridgeScores)
admin.site.register_view('retabPastaBridge', 'Tabulate Final Pasta Bridge Scores', view=RetabulatePastaBridgeScores)

class PastaBridgeScoreForm(ScoreForm):
    def __init__(self, *args, **kwargs):

        super(PastaBridgeScoreForm, self).__init__(*args, **kwargs)
        standard_events = Event.objects.filter(event_score_type='PBR').distinct()

        standard_events = standard_events.filter(owners__in=self.current_groups)

        event_widget = self.fields['event'].widget

        choices = []
        for element in standard_events:
            choices.append((element.id, element.name))
        event_widget.choices = choices

class PastaBridgeScoreAdmin(ScoreAdmin):
    form = PastaBridgeScoreForm
    def get_form(self, request, obj=None, **kwargs):
        form = super(PastaBridgeScoreAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        form.current_groups = request.user.groups.all()

        return form
    pass


# Chemical Car
def RetabulateChemicalCarScores(request):
    chemical_car_scores = ChemicalCarScore.objects.all()
    
    for chemical_car_score in chemical_car_scores:
        chemical_car_score.save()
    return HttpResponseRedirect('/admin/')
RetabulateChemicalCarScores = staff_member_required(RetabulateChemicalCarScores)
admin.site.register_view('retabChemicalCar', 'Tabulate Final Chemical Car Scores', view=RetabulateChemicalCarScores)

class ChemicalCarScoreForm(ScoreForm):
    def __init__(self, *args, **kwargs):

        super(ChemicalCarScoreForm, self).__init__(*args, **kwargs)
        standard_events = Event.objects.filter(event_score_type='CCAR').distinct()

        standard_events = standard_events.filter(owners__in=self.current_groups)

        event_widget = self.fields['event'].widget

        choices = []
        for element in standard_events:
            choices.append((element.id, element.name))
        event_widget.choices = choices

class ChemicalCarScoreAdmin(ScoreAdmin):
    form = ChemicalCarScoreForm
    def get_form(self, request, obj=None, **kwargs):
        form = super(ChemicalCarScoreAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        form.current_groups = request.user.groups.all()

        return form
    pass

# Weight Lifting
def RetabulateWeightLiftingScores(request):
    weight_lifting_scores = WeightLiftingScore.objects.all()
    
    for weight_lifting_score in weight_lifting_scores:
        weight_lifting_score.save()
    return HttpResponseRedirect('/admin/')
RetabulateWeightLiftingScores = staff_member_required(RetabulateWeightLiftingScores)
admin.site.register_view('retabWeightLifting', 'Tabulate Final Weight Lifting Scores', view=RetabulateWeightLiftingScores)

class WeightLiftingScoreForm(ScoreForm):
    def __init__(self, *args, **kwargs):

        super(WeightLiftingScoreForm, self).__init__(*args, **kwargs)
        standard_events = Event.objects.filter(event_score_type='WLFT').distinct()

        standard_events = standard_events.filter(owners__in=self.current_groups)

        event_widget = self.fields['event'].widget

        choices = []
        for element in standard_events:
            choices.append((element.id, element.name))
        event_widget.choices = choices

class WeightLiftingScoreAdmin(ScoreAdmin):
    form = WeightLiftingScoreForm
    def get_form(self, request, obj=None, **kwargs):
        form = super(WeightLiftingScoreAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        form.current_groups = request.user.groups.all()

        return form
    pass

# Indoor Catapults
def RetabulateIndoorCatapultsScores(request):
    indoor_catapults_scores = IndoorCatapultsScore.objects.all()
    
    for indoor_catapults_score in indoor_catapults_scores:
        indoor_catapults_score.save()
    return HttpResponseRedirect('/admin/')
RetabulateIdoorCatapultsScores = staff_member_required(RetabulateIndoorCatapultsScores)
admin.site.register_view('retabIndoorCatapults', 'Tabulate Final Indoor Catapults Scores', view=RetabulateIndoorCatapultsScores)

class IndoorCatapultsScoreForm(ScoreForm):
    def __init__(self, *args, **kwargs):

        super(IndoorCatapultsScoreForm, self).__init__(*args, **kwargs)
        standard_events = Event.objects.filter(event_score_type='ICT').distinct()

        standard_events = standard_events.filter(owners__in=self.current_groups)

        event_widget = self.fields['event'].widget

        choices = []
        for element in standard_events:
            choices.append((element.id, element.name))
        event_widget.choices = choices

class IndoorCatapultsScoreAdmin(ScoreAdmin):
    form = IndoorCatapultsScoreForm
    def get_form(self, request, obj=None, **kwargs):
        form = super(IndoorCatapultsScoreAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        form.current_groups = request.user.groups.all()

        return form
    pass


"""
def RetabulateVolcanoScores(request):
    volcano_scores = VolcanoScore.objects.all()

    for volcano_score in volcano_scores:
        volcano_score.save()
    return  HttpResponseRedirect('/admin/')
RetabulateEggDropScores = staff_member_required(RetabulateVolcanoScores)
admin.site.register_view('retabVolcanoScores','Tabulate Final Volcano Scores', view=RetabulateVolcanoScores)

class VolcanoScoreForm(ScoreForm):
    def __init__(self, *args, **kwargs):

        super(VolcanoScoreForm, self).__init__(*args, **kwargs)
        standard_events = Event.objects.filter(event_score_type='VLN').distinct()

        standard_events = standard_events.filter(owners__in=self.current_groups)

        event_widget = self.fields['event'].widget

        choices = []
        for element in standard_events:
            choices.append((element.id, element.name))
        event_widget.choices = choices

class VolcanoScoreAdmin(ScoreAdmin):
    form = VolcanoScoreForm
    def get_form(self, request, obj=None, **kwargs):
        form = super(VolcanoScoreAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        form.current_groups = request.user.groups.all()

        return form
    pass
"""

admin.site.register(DrillingMudScore, DrillingMudAdmin)
admin.site.register(GravityCarScore, GravityCarScoreAdmin)
admin.site.register(EggDropScore, EggDropScoreAdmin)
admin.site.register(SkyscraperScore, SkyscraperScoreAdmin)
admin.site.register(PastaBridgeScore, PastaBridgeScoreAdmin)
admin.site.register(ChemicalCarScore, ChemicalCarScoreAdmin)
admin.site.register(WeightLiftingScore, WeightLiftingScoreAdmin)
admin.site.register(IndoorCatapultsScore, IndoorCatapultsScoreAdmin)
"""
admin.site.register(VolcanoScore, VolcanoScoreAdmin)
"""