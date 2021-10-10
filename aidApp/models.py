from django.db import models
from django.utils import timezone as tz, tree
from django.contrib.auth.models import User
from django.db.models.fields import TextField
from django.db.models.deletion import CASCADE, SET, SET_NULL
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.forms import widgets
import datetime
from django.utils.dateparse import parse_date
from phone_field import PhoneField

class FAQ(models.Model):

    question = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return self.question


class Contact(models.Model):

    CHOICES = [(None, "Nature of Inquiry"),('Feedback','Feedback'),('Career','Career'),('Support','Support'),]

    fname = models.CharField(max_length=50, null=True)
    lname = models.CharField(max_length=50, null=True)
    email = models.EmailField(max_length=60, null=True)
    inquiry = models.CharField(choices=CHOICES, default= "Feedback", max_length=8)
    subject = models.CharField(max_length=50, null=True)
    comment = models.TextField(max_length=400, null=True)

    def __str__(self):
        return self.subject



class Patient(models.Model):
    
    patient = models.OneToOneField(User, on_delete=models.CASCADE)
    telephone = PhoneField(blank=True, help_text='Patient phone number')
    # D_O_B = models.DateField(default=tz.now)
    D_O_B = models.CharField(max_length=20)
    # age = models.CharField(max_length=5)
    registration_date = models.DateTimeField(auto_now_add=True)
    sex = models.CharField(max_length=20)
    marital_status = models.CharField(max_length=50) 
    race_or_ethnicity = models.CharField(max_length=60, blank=True, null=True)
    smoker = models.CharField(max_length=3, default='No')
    @property
    def age(self):
        return tz.now().year - parse_date(self.D_O_B).year
    
    def __str__(self):
        return self.patient.get_full_name() 


class Patient_Contact_Info(models.Model):
    
    patient = models.OneToOneField('Patient', null=True, on_delete=models.CASCADE)
    address_1 = models.CharField(max_length= 30, blank=True, null=True)
    address_2 = models.CharField(max_length= 30,blank=True, null=True)
    city = models.CharField(max_length= 30,blank=True, null=True)
    state = models.CharField(max_length= 30,blank=True, null=True)
    zip_code = models.CharField(max_length= 10,blank=True, null=True)
    
    
class Emergency_Contact_Info(models.Model):

    patient = models.OneToOneField('Patient', null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length= 30, blank=True, null=True) 
    relation = models.CharField(max_length=30,blank=True, null=True)
    phone_number = models.CharField(max_length= 30, blank=True, null=True)
    email = models.CharField(max_length= 30, blank=True, null=True)
    address_1 = models.CharField(max_length= 30, blank=True, null=True)
    address_2 = models.CharField(max_length= 30, blank=True, null=True)
    city = models.CharField(max_length= 30, blank=True, null=True)
    state = models.CharField(max_length= 30, blank=True, null=True)
    zip_code = models.CharField(max_length= 10, blank=True, null=True)
    


class Medical_History(models.Model):

    patient = models.ForeignKey('Patient', null=True, on_delete=models.CASCADE)
    health_practitioner = models.ForeignKey('Health_Practitioner', null=True, on_delete=models.SET_NULL)
    date_visited = models.DateField(default=tz.now)
    patient_concerns = TextField(blank=True, null=True)
    heart_rate = models.IntegerField(blank=True, null=True)
    bP_systolic = models.IntegerField(blank=True, null=True)
    bP_diastolic = models.IntegerField(blank=True, null=True)
    spO2 = models.IntegerField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    bmi = models.FloatField(blank=True, null=True)
    prescriptions = models.TextField(blank=True, null=True)
    test_results = models.TextField(blank=True, null=True)
    health_practitioner_comments = models.TextField(blank=True, null=True)


class Health_Practitioner(models.Model):
    
    health_practitioner = models.OneToOneField(User, null=False, on_delete=models.CASCADE)
    clinics = models.ForeignKey('Clinic', blank=True, null=True,on_delete=models.CASCADE)
    professional_title = models.CharField(default= "Dr. ", max_length=4)
    professional_suffix = models.CharField(default= " MD", max_length=4)
    telephone = models.CharField(max_length=20)
    specialty = models.TextField(max_length=200)
    consultation_times = models.TextField(default="Monday - 10:00am to 11:00am", max_length=600)
    insurance_accepted = models.CharField(default='Blue Cross', max_length=500)
    languages = models.CharField(default='English', max_length=60)
    accepting_new_patients = models.CharField(default='Yes', max_length=3)
    reviews = models.IntegerField(default=29)
    rating_reviews = models.FloatField(default=4.7)
    patient_comments = models.IntegerField(default=25)
    appointments_pending = models.IntegerField(default=0)
    appointments_approved = models.IntegerField(default=0)

    def __str__(self):
        return self.health_practitioner.get_full_name()
    

class Feedback(models.Model):

    # patient = models.ForeignKey(Patient, null=True, on_delete=SET_NULL)
    fullname = models.CharField(max_length=200)
    email = models.EmailField(max_length=60)
    response_type = models.CharField(max_length=50)
    # response_type = models.TextField(default='complaint',choices=(('complaint', 'complaint'), ('other', 'other')))
    # subject = models.CharField(max_length=100)
    message = models.TextField(max_length=400)

    def __str__(self):
        return self.fullname


class Pharmacy(models.Model):

    name = models.CharField(max_length=100)
    service_options = models.CharField(max_length=50)
    located_in = models.TextField(max_length=254)
    address = models.TextField(max_length=254)
    hours = models.TextField(max_length=254)
    telephone = models.CharField(max_length=20)
    website = models.URLField(max_length=100)
    directions = models.TextField(max_length=254)
    
    def __str__(self):
        return self.name

class Clinic(models.Model):

    name = models.CharField(max_length=40)
    website = models.URLField(max_length=100)
    located_in = models.TextField(max_length=100)
    address = models.TextField(max_length=254)
    hours = models.TextField(max_length=254) 
    appointments_url = models.URLField(max_length=100)
    telephone = models.CharField(max_length=20)
    question_answer = models.TextField(max_length=254)
    availability = models.TextField(default="Monday, Tuesday", max_length=60)

    #consultation times - specific to each Clinic
    
    def __str__(self):
        return self.name
    

class Appointment(models.Model):

    TIMESLOTS = [(0, '9:00 AM'),
                (1, '10:00 AM'),
                (2, '11:00 AM'),
                (3, '12:00 PM'),
                (4, '1:00 PM'),
                (5, '2:00 PM'),
                (6, '3:00 PM'),
                (7, '4:00 PM'),
                (8, '5:00 PM')]
    
    STATUS = [(0, 'Pending'), (1, 'Accept'), (2, 'Decline')]

    health_practitioner = models.ForeignKey(Health_Practitioner, null=True, on_delete=models.CASCADE) 
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    appointment_date = models.DateField(default=tz.now)
    timeslots = models.IntegerField(choices=TIMESLOTS, default=0)
    appt_reason = TextField(default= 'Annual Physical Examination', max_length=200)
    app_status = models.IntegerField(choices=STATUS, default=0)
  
    def __str__(self):
        return "{} ,{} ,{} ,{} ,{}".format(self.patient, self.appointment_date, self.time, self.appt_reason, self.health_practitioner, self.status)
    
    @property
    def time(self):
        return self.TIMESLOTS[self.timeslots][1]

    @property
    def status(self):
        return self.STATUS[self.app_status][1]

     
