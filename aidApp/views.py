from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from datetime import date
from django.utils import timezone as tz
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail, get_connection
from django.conf import settings
from django.db.models import Q
from .models import Feedback, Patient, Health_Practitioner, FAQ, Appointment, Clinic
from .forms import CreateContactForm#, AppUpdateForm, AppRetrieveForm ,AppCreateForm, DocProfileForm 

# Create your views here.

# Landing page 
def index(request):
    return render(request, 'index.html')

# About Us page 
def about_us(request):
    return render(request, 'about-us.html')

def faq(request):

    faqs = FAQ.objects.all()
    context = {
        "Faqs":faqs

    }
    return render(request,'aidApp/faq.html',context)

@login_required
def doctor_dash_view(request):
    context = {
        'doctor': Health_Practitioner.objects.all()
    }
    return render(request, 'aidApp/doctor/doctor-dash.html', context)

def doctor_profile_view(request):
    return render(request, 'aidApp/doctor/doctor-profile.html')

def doctor_patient_view(request):
    return render(request, 'aidApp/doctor/doctor-patient.html')

def doctor_search_view(request):
    if request.method == "POST":
        search = request.POST.get('search')
        patients =Patient.objects.filter(Q(patient__first_name__icontains=search) | Q(patient__last_name__icontains=search))
    else:
        patients = Patient.objects.all()

    context = {
        'patients': patients,
        
    }
    return render(request, 'aidApp/doctor/doctor-search.html', context)

def doctor_appointment_view(request):
    return render(request, 'aidApp/doctor/doctor-appointment.html')

def doctor_schedule_view(request):
    return render(request, 'aidApp/doctor/doctor-schedule.html')
    
def doctor_schedule_week_view(request):
    return render(request, 'aidApp/doctor/doctor-schedule-week.html')

@login_required
def doctor_support_view(request):

    user = request.user.username
    currentuser = User.objects.get(username=user)
    fullname = f"{currentuser.first_name} {currentuser.last_name}" 
    email = currentuser.email
    
    context = {
        'fullname': fullname,
        'email': email,
    }
    
    if request.method == "POST":
        if request.POST.get('fullname') and request.POST.get('message'):
            support = Feedback()
            support.fullname = request.POST.get('fullname')
            support.email = request.POST.get('email')
            support.response_type = request.POST.get('complaint')
            support.message = request.POST.get('message')
            support.save()
            send_mail(
                'Contact Support',
                'Your message has been received.  If needed, someone will follow up with you shortly.  Thank you!',               
                'devops4zuri@gmail.com',
                [email],
                fail_silently=False,
                )
            return redirect('doctor-support-success')
        else: 
            messages.error(request, 'Message section can not be empty.  Submit unsuccessful.')
            return render(request, 'aidApp/doctor/doctor-support.html', context) 
    else:
        return render(request, 'aidApp/doctor/doctor-support.html', context)

def doctor_support_success_view(request):
    return render(request, 'aidApp/doctor/doctor-support-feedback.html')

def doctor_signup_view(request):
    return render(request, 'aidApp/doctor/doctor-signup.html')



@login_required
def support_view(request):

    user = request.user.username
    currentuser = User.objects.get(username=user)
    fullname = f"{currentuser.first_name} {currentuser.last_name}" 
    email = currentuser.email
    
    context = {
        'fullname': fullname,
        'email': email,
    }
    
    if request.method == "POST":
        if request.POST.get('fullname') and request.POST.get('message'):
            support = Feedback()
            support.fullname = request.POST.get('fullname')
            support.email = request.POST.get('email')
            support.response_type = request.POST.get('complaint')
            support.message = request.POST.get('message')
            support.save()
            send_mail(
                'Contact Support',
                'Your message has been received.  If needed, someone will follow up with you shortly.  Thank you!',
                'devops4zuri@gmail.com',
                [email],
                fail_silently=False,
                )
            return redirect('support-success')
        else: 
            messages.error(request, 'Message section can not be empty.  Submit unsuccessful.')
            return render(request, 'aidApp/patient/patient-support.html', context) 
    else:
        return render(request, 'aidApp/patient/patient-support.html', context)

def support_success_view(request):
    return render(request, 'aidApp/patient/patient-support-feedback.html')


@login_required
def CreateContact(request):
    
    context = {}
        
    if request.method == 'POST':
         form = CreateContactForm(request.POST)
         if form.is_valid():
             
             subject = form.cleaned_data['subject']
             message = form.cleaned_data['comment']
             sender = form.cleaned_data['email']
             
             administrators = []
             for admin in User.objects.filter(is_superuser=True):
                administrators.append(admin.email)
            
             con = get_connection(settings.EMAIL_BACKEND)
             send_mail(subject,
                      message,
                      sender,
                      administrators,
                      connection=con            
             )
             form.save()
             messages.success(request, "Your message was submitted successfully! Thank you.")
                     
         else:
             
             return render(request,'aidApp/contact/contact.html',{'form': form})
 
    context = {'form': CreateContactForm()}
    return render(request, 'aidApp/contact/contact.html', context) 


