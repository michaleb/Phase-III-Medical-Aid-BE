from typing import Text
from django import forms
from datetime import date
from django.db.models import fields
from django.forms import widgets
from django.forms import ModelForm, TextInput, EmailInput
from datetimewidget.widgets import DateWidget
from django.forms.widgets import Select, Textarea
from aidApp.models import Contact, Appointment, Health_Practitioner, Clinic


class CreateContactForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = '__all__'
        widgets = {'fname': TextInput(attrs={'class': "input-container", 'style': "margin-right: 100px"}),
                   'lname': TextInput(attrs={'class': "input-container"}),
                   'email': EmailInput(attrs={'class': "input-container", 'style': "margin-right: 100px"}),
                   'inquiry': Select(attrs={'class':"dropdown", 'style': "margin-right: 56px", 'width': '100%', 'text-align': 'center'}),
                   'subject': TextInput(attrs={'class': "input-container"}),
                   'comment': Textarea(attrs={'class':"bottom-form", 'style': "width: 740px; height: 300px"})        
        }


class DocProfileForm(forms.ModelForm):

    class Meta:
        model = Health_Practitioner
        exclude = ['appointments_approved', 'appointments_pending']
          


class AppCreateForm(forms.ModelForm):
    
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'timeslots', 'appt_reason']
        
        widgets = {
            'appointment_date': DateWidget(
                #attrs={'id': 'appointment_date'}, usel10n=False, bootstrap_version=3,
                attrs={'class':'date-input'}, usel10n=False, bootstrap_version=3,
        
                options={
                    'minView': 2,  # month view
                    'maxView': 3,  # year view
                    'weekStart': 0,
                    'todayHighlight': True,
                    'format': 'yyyy-mm-dd',
                    'daysOfWeekDisabled': [0],
                    'startDate': date.today().strftime('%Y-%m-%d'),
                }),
                               
        }
        
    
