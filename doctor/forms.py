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
        