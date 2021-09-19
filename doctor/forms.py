from django import forms
from aidApp.models import Health_Practitioner

class HealthPractitionerForm(forms.ModelForm):
    CHOICES = (('1', 'Blue Cross'), ('2', 'Blue Shield'), ('3', 'Cigna'), 
              ('4', 'Health Net'), ('5', 'Medicare'), ('6', 'World Health'), 
              ('7', 'Care First'))

    insurance_accepted = forms.MultipleChoiceField(choices = CHOICES)

    class Meta:

        model = Health_Practitioner
        # fields = '__all__' # to import all fields
        exclude = ['health_practitioner','professional_title','professional_suffix','reviews','rating_reviews','patient_comments', 'appointments_pending','appointments_approved']
