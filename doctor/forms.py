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
        fields = "__all__"
        widgets = {'app_status': Select(attrs={'class':"review"}, choices=[(0 ,'Review'), (1 ,'Accept')])}
        


class HealthPractitionerForm(forms.ModelForm):
    CHOICES = (('Blue Cross', 'Blue Cross'), ('Blue Shield', 'Blue Shield'), ('Cigna', 'Cigna'), 
              ('Health Net', 'Health Net'), ('Medicare', 'Medicare'), ('World Health', 'World Health'), 
              ('Care First', 'Care First'))

    insurance_accepted = forms.MultipleChoiceField(choices = CHOICES)

    class Meta:

        model = Health_Practitioner
        # fields = '__all__' # to import all fields
        exclude = ['health_practitioner','professional_title','professional_suffix','reviews','rating_reviews','patient_comments', 'appointments_pending','appointments_approved']
