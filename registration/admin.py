from registration.models import School, Teacher, Participant, Team
from django.contrib import admin
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from math import ceil
from scoring.models import PreRegistration
from django.conf import settings
from django.views.decorators.cache import cache_page
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing 
from reportlab.graphics.barcode.qr import QrCodeWidget 
from reportlab.graphics import renderPDF    
from reportlab.graphics.barcode import code128
import time
import csv

class TeamAdmin(admin.ModelAdmin):
    list_filter = ('school', 'division',)
    list_display = ('name', 'school', 'division', 'id')
    search_fields = ('name', 'id')

class SchoolAdmin(admin.ModelAdmin):
    list_filter = ('school_type',)
    list_display = ('name', 'school_type',)
    search_fields = ('name',)


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('teacher',)
    filter_horizontal = ('teams',)
    search_fields = ( 'name',)

    
    
admin.site.register(Team, TeamAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Teacher)
admin.site.register(Participant, ParticipantAdmin)


def GetParticipantLabels(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')

    response['Content-Disposition'] = 'attachment; filename="participant_labels_' + time.strftime("%b_%d_%Y_%H_%M", time.gmtime()) + '.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, pagesize=letter, pageCompression=1,)
    p.setFont('Helvetica', 12)
    width, height = letter
    
    
    
    LABELW = 8 * inch
    LABELSEP = 1 * inch
    LABELH = 3 * inch
    
    data = []
    students = Participant.objects.all().order_by('-name',)
    
    for student in students:
        team_names = []
        first_school = ''
        for team in student.teams.all():
            first_school=team.school.name
            obj = {'team_id':team.id, 'team_name':team.name}
            team_names.append(obj)
        
        label = {'name':student.name,'sid':student.id, 'teams':team_names,'school':first_school}
        data.append(label)

    
    def LabelPosition(ordinal):
        y, x = divmod(ordinal, 1)
        x = 14 + x * LABELSEP
        y = 756 - y * LABELH
        return x, y


    total_labels = len(data)
    sheets = int(ceil(total_labels / 3.0))
    
    for i in range(0, sheets):
        for pos in range(0, 3):
            if  data:
                participant = data.pop()
                
            x, y = LabelPosition(pos)
            p.rect(x, y, LABELW, -LABELH)
            p.rect(x, y, LABELW / 2, -LABELH)
            tx = p.beginText(x + 25, y - 50)
            p.drawImage(settings.STATIC_ROOT+'ku/jayhawk.png', x+200, y-210, preserveAspectRatio=True)
       
            tx.setFont('Courier', 32, 32)
            
          
            
            name_parts = participant['name'].split()
            name_string = ''
            for name_part in name_parts:
                name_string = name_string + '\n' + name_part
            tx.textLines(name_string)
            p.drawText(tx)
            
            ts = p.beginText(x+25,y-135)
            ts.setFont('Courier', 16, 16)
            ts.textLine(participant['school'][:25])
            p.drawText(ts)
            
            
            team_string = ''
            
            for team in participant['teams']:
                team_string = team_string + '\n' + team['team_name'] + ' : ' + str(team['team_id'])
                for event_team in PreRegistration.objects.filter(teams__name=team['team_name']):
                    team_string = team_string + '\n' + event_team.event.name
                team_string =  team_string + '\n*******************'
        
       
            tx = p.beginText(x + 325, y - 30)
            tx.setFont('Courier', 12, 12)
            tx.textLines(team_string)
            
            
            
            p.drawText(tx)
        p.addPageLabel(p.getPageNumber(),style='    DECIMAL_ARABIC_NUMERALS' )
        p.showPage()


    # Close the PDF object cleanly, and we're done.
   
    p.save()
    return response

    
GetParticipantLabels = staff_member_required(GetParticipantLabels)
admin.site.register_view('labels/GetAllParticipantLabels', GetParticipantLabels)        
    
def get_school_participant_list(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="participant_team_list_' + time.strftime("%b_%d_%Y_%H_%M", time.gmtime()) + '.csv"'
    writer = csv.writer(response,dialect='excel')  
    data = []
    for school in School.objects.all():
        for team in Team.objects.filter(school=school):
            students = [student.name for student in Participant.objects.filter(teams=team)]
            l = students
            l.insert(0,team.name)
            l.insert(0,school.name)
            writer.writerow(l)
    return response

get_school_participant_list = staff_member_required(get_school_participant_list)
admin.site.register_view('csv/GetSchoolParticipantCsv', get_school_participant_list)
    
