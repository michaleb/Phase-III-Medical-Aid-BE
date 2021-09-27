from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
import datetime
from aidApp.models import Feedback, Patient, Health_Practitioner, Clinic, Pharmacy

# Create your views here.

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
            return render(request, 'patient/patient-support.html', context) 
    else:
        return render(request, 'patient/patient-support.html', context)

def support_success_view(request):
    return render(request, 'patient/patient-support-feedback.html')


@login_required
def patient_dash_view(request):
    user = User.objects.get(username = request.user.username)
    patient = Patient.objects.get(patient = user)
    
    context = {
        'patient': patient
    }

    return render(request, 'patient/patient-dash.html', context)

def patient_doctor_view(request):
    if request.method == "POST":
        search = request.POST.get('search')
        # specialty_search = request.POST.get('specialty')
        doctors = Health_Practitioner.objects.filter(Q(health_practitioner__first_name__icontains=search) \
                  | Q(health_practitioner__last_name__icontains=search) | Q(clinics__name__icontains=search) \
                  | Q(specialty__icontains=search))
    else:
        doctors = Health_Practitioner.objects.all()
    
    context = {
        'doctors': doctors,
        
    }
    return render(request, 'patient/patient-doctor.html', context)

def patient_profile_view(request):
    user = User.objects.get(username = request.user.username)
    patient = Patient.objects.get(patient = user)
    instance = get_object_or_404(Patient, patient=request.user)

    if request.method == 'POST':
        patient.D_O_B = request.POST.get('birthdate')
        patient.sex = request.POST.get('gender')
        patient.marital_status = request.POST.get('marital')
        patient.save()


    context = {
        'patient': patient,
        
    }
    return render(request, 'patient/patient-profile.html', context)

def patient_clinic_view(request):
    if request.method == "POST":
        search = request.POST.get('search')
        if request.POST.get('clinic-pharmacy') == 'clinics':
            query = Clinic.objects.filter(name__icontains=search)
        elif request.POST.get('clinic-pharmacy') == 'pharmacies':
            query = Pharmacy.objects.filter(name__icontains=search)
    else:
        query = Clinic.objects.all()

    location = request.POST.get('clinic-pharmacy')
    
    context = {

        'query': query,
        'location': location,

    }
    
    return render(request, 'patient/patient-clinic.html', context)

def clinic_info_view(request, location, pk):
    if location == 'clinics':
        place = get_object_or_404(Clinic, id=pk)
    elif location == 'pharmacies':
        place = get_object_or_404(Pharmacy, id=pk)
    else:
        place = get_object_or_404(Clinic, id=pk)

    context = {

        'place': place,
        
        

     }

    return render(request, 'patient/patient-clinic-info.html', context)