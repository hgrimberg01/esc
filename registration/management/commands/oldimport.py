from django.core.management.base import BaseCommand, CommandError
import MySQLdb as mdb2
from registration.models import Team,Participant,School
from scoring.models import Event,PreRegistration


    
class Command(BaseCommand):
    args = ''
    help = 'Closes the specified poll for voting'
    new_db_name = 'intermediary'
    new_db_user = 'root'
    new_db_password = '1234'
    new_db_host = 'localhost'
    new_con = mdb2.connect(new_db_host, new_db_user, new_db_password, new_db_name)
    
    def handle(self, *args, **options):
        print 'test'
        cursor = self.new_con.cursor()
        School.objects.all().delete()
        cursor.execute("SELECT `school_name`,`school_type` FROM `school` GROUP BY `school_name`;")
        school_rs = cursor.fetchall()
        for school in school_rs:
            new_school = School(name=school[0],school_type=school[1])
            new_school.save()
        cursor.execute("SELECT `team`.`team_name`,`school`.`school_name`,`school`.`school_type` FROM `team` JOIN `school_to_team` JOIN `school` WHERE `team`.`team_id` = `school_to_team`.`team_id` AND `school`.`school_id` = `school_to_team`.`school_id`;")
        team_rs = cursor.fetchall()
        
        Team.objects.all().delete()
        for team in team_rs:
            new_team = Team(name=team[0],division=team[2],school=School.objects.get(name=team[1]))
            new_team.save()
    
        cursor.execute("SELECT `student_name` FROM `student`;")
        student_rs = cursor.fetchall()
        Participant.objects.all().delete()
        for student in student_rs:
            new_student = Participant(name=student[0])
            new_student.save()
        
        cursor.execute("SELECT `student`.`student_name`,`team`.`team_name` FROM `student` JOIN `student_to_team` JOIN `team` WHERE `team`.`team_id`=`student_to_team`.`team_id` and `student`.`student_id`=`student_to_team`.`student_id`;")
        team_student_rs = cursor.fetchall()
        
        for team_student in team_student_rs:
            for student in Participant.objects.filter(name=team_student[0]):
                for team in Team.objects.filter(name=team_student[1]):
                    student.teams.add(team)
                    student.save()
                    
        cursor.execute("SELECT `event_name` FROM `events`;")
        event_rs = cursor.fetchall()
        
        Event.objects.all().delete()
        for event in event_rs:
            event = Event(name=event[0],max_score=100.0,min_score=0.0,event_score_type='STD')
            event.save()
        
        cursor.execute("SELECT `events`.`event_name`,`team`.`team_name` FROM `events` JOIN `team_to_event` JOIN `team` WHERE `team`.`team_id`=`team_to_event`.`team_id` and `events`.`event_id`=`team_to_event`.`event_id`;")
        event_team_rs = cursor.fetchall()
        
        PreRegistration.objects.all().delete()
        for event_team in event_team_rs:
            for team in Team.objects.filter(name=event_team[1]):
                for event in Event.objects.filter(name=event_team[0]):
                    reg = PreRegistration(teams=team,event=event)
                    reg.save()
        
                    
                
                    
    
            
        
    
        
        