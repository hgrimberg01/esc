# Create your views here.

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.forms import ModelForm
from django import forms
from scoring.models import Event
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail

def reg_usr(request):
    if request.method == 'POST': # If the form has been submitted...
        form = UserRegForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            info = form.cleaned_data
            password = User.objects.make_random_password()
            new_user = User(username=info['username'],first_name=info['first_name'],last_name=info['last_name'],email=info['email'],is_staff=True)
            new_user.set_password(password)
            new_user.save()
            for event in info['events']:
                try:
                    grp = Group.objects.get(name=event.name)
                    new_user.groups.add(grp)
                except:
                    print 'err'
            message = 'Thank you '+new_user.first_name + ' ' + new_user.last_name + '\n'
            message = message + 'Your username is '+new_user.username + '\n'   
            message = message + 'Your temporary is '+password + '\n'    
            message = message + 'You may now login at http://expo.zapto.org/admin/'+'\n'
            message = message + 'Please remember to change your password(top right corner when logged in)'      
            send_mail('EXPO Scoring System User Info', message, 'scoring-system@' + 'score-system@outlook.com',(new_user.email,), fail_silently=False)
            new_user.save()
            return HttpResponseRedirect('/register/thanks/') # Redirect after POST
    else:
        data = {'subject': 'hello'}
        form = UserRegForm()

    return render(request, 'register/register.html', {
        'form': form,
    })
class UserRegForm(ModelForm):
    error_css_class='alert alert-error'

    events = forms.ModelMultipleChoiceField(queryset=Event.objects.all())
    class Meta:
        model = User
        fields = ('username', 'first_name','last_name','email',)
    
    def clean_email(self):
        try:
            
            user = User.objects.get(email=self.cleaned_data['email'])
        except:
           return self.cleaned_data['email'] 
        else:
           raise forms.ValidationError('Email Is Already Registered')
            
    

