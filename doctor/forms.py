from django import forms
from datetime import date
from django.db.models import fields
from django.forms import widgets
from django.forms import ModelForm, TextInput, EmailInput
#from datetimewidget.widgets import DateWidget
from django.forms.widgets import Select, Textarea
from aidApp.models import Contact, Appointment, Health_Practitioner, Clinic, Patient


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
