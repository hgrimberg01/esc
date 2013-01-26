from registration.models import School,Teacher,Participant,Team
from django.contrib import admin

class TeamAdmin:
    list_filter = ('name',)

admin.site.register(Team,TeamAdmin)
admin.site.register(School)
admin.site.register(Teacher)
admin.site.register(Participant)
## Define an inline admin descriptor for UserProfile model
## which acts a bit like a singleton
#class UserProfileInline(admin.StackedInline):
#    model = TeacherProfile
#    can_delete = False
#    verbose_name_plural = 'TeacherProfile'
#    
## Define a new User admin
#class UserAdmin(UserAdmin):
#    inlines = (UserProfileInline, )
#
## Re-register UserAdmin
#admin.site.unregister(User)
#admin.site.register(User, UserAdmin)
###