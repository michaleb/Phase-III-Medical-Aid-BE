from django import forms
from datetime import date
from django.db.models import fields
from django.forms import widgets
from django.forms import ModelForm, TextInput, EmailInput, DateInput
#from datetimewidget.widgets import DateWidget
from django.forms.widgets import Select, Textarea
from aidApp.models import Contact, Appointment, Health_Practitioner, Clinic, Patient
#from .models import Event

class ConsultationForm(forms.ModelForm):
    

    class Meta:
        model = Appointment
        exclude = ['health_practitioner', 'patient', 'appointment_date', 'timeslots', 'appt_reason']
        #fields = '__all__'
        #widgets = {'app_status': {'class':"review"}} #, choices=[(0 ,'Pending'), (1 ,'Accept'), (2, 'Decline')])}
        app_status = forms.IntegerField()
        
    

class HealthPractitionerForm(forms.ModelForm):
    CHOICES = (('Blue Cross', 'Blue Cross'), ('Blue Shield', 'Blue Shield'), ('Cigna', 'Cigna'), 
              ('Health Net', 'Health Net'), ('Medicare', 'Medicare'), ('World Health', 'World Health'), 
              ('Care First', 'Care First'))

    insurance_accepted = forms.MultipleChoiceField(choices = CHOICES)

    class Meta:

        model = Health_Practitioner
        # fields = '__all__' # to import all fields
        exclude = ['health_practitioner','professional_title','professional_suffix','reviews','rating_reviews','patient_comments', 'appointments_pending','appointments_approved']



class EventForm(ModelForm):
  class Meta:
    model = Appointment
    # datetime-local is a HTML5 input type, format to make date time show on fields
    # widgets = {
    #   'appointment_date': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%d'),
    #   'timeslots': DateInput(attrs={'type': 'datetime-local'}, format='T%H:%M'),
    # }
    # fields = '__all__'
    exclude = ['app_status']

  def __init__(self, *args, **kwargs):
    super(EventForm, self).__init__(*args, **kwargs)
    # input_formats to parse HTML5 datetime-local input to datetime field
    # self.fields['appointment_date'].input_formats = ('%Y-%m-%d',)
    # self.fields['timeslots'].input_formats = ('T%H:%M',)