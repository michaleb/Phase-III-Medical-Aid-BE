from django import forms
from aidApp.models import Health_Practitioner

class HealthPractitionerForm(forms.ModelForm):
    CHOICES = (('Blue Cross', 'Blue Cross'), ('Blue Shield', 'Blue Shield'), ('Cigna', 'Cigna'), 
              ('Health Net', 'Health Net'), ('Medicare', 'Medicare'), ('World Health', 'World Health'), 
              ('Care First', 'Care First'))

    insurance_accepted = forms.MultipleChoiceField(choices = CHOICES)

    class Meta:

        model = Health_Practitioner
        # fields = '__all__' # to import all fields
        exclude = ['health_practitioner','professional_title','professional_suffix','reviews','rating_reviews','patient_comments', 'appointments_pending','appointments_approved']
