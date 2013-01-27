from registration.models import School,Teacher,Participant,Team
from django.contrib import admin

class TeamAdmin(admin.ModelAdmin):
    list_filter = ('school','division',)
    list_display = ('name','school','division','id')
    search_fields = ('name','id')

class SchoolAdmin(admin.ModelAdmin):
    list_filter = ('school_type',)
    list_display=('name','school_type',)
    search_fields=('name',)


class ParticipantAdmin(admin.ModelAdmin):
    list_display=('name',)
    list_filter=('teacher',)
    search_fields=('teacher','name',)

    
    
admin.site.register(Team,TeamAdmin)
admin.site.register(School,SchoolAdmin)
admin.site.register(Teacher)
admin.site.register(Participant,ParticipantAdmin)
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