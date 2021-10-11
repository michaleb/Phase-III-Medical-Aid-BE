from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
import datetime, ast
from aidApp.models import Feedback, Patient, Health_Practitioner, Clinic, Appointment
from .forms import ConsultationForm, HealthPractitionerForm


# Create your views here.

@login_required
def doctor_dash_view(request):
    user = User.objects.get(username = request.user.username)
    doctor = Health_Practitioner.objects.get(health_practitioner = user)
    
    context = {
        'doctor': doctor
    }
    return render(request, 'doctor/doctor-dash.html', context)

def doctor_profile_view(request):
    user = User.objects.get(username = request.user.username)
    doctor = Health_Practitioner.objects.get(health_practitioner = user)
    insurance_accepted = ast.literal_eval(doctor.insurance_accepted)
    context = {
        'doctor': doctor,
        'insurance_accepted': insurance_accepted
        
    }
    return render(request, 'doctor/doctor-profile.html', context)
    

def doctor_patient_view(request, pk):
    
    patient = get_object_or_404(Patient, id=pk)

    return render(request, 'doctor/doctor-patient.html', context={ 'patient': patient})

def doctor_consultation_view(request):
    return render(request, 'doctor/doctor-consultations.html')

def doctor_search_view(request):
    if request.method == "POST":
        search = request.POST.get('search')
        patients = Patient.objects.filter(Q(patient__first_name__icontains=search) | Q(patient__last_name__icontains=search))
    else:
        patients = Patient.objects.all()
    
    context = {
        'patients': patients,
        
    }
    return render(request, 'doctor/doctor-search.html', context)

def doctor_appointment_view(request):
    return render(request, 'doctor/doctor-appointment.html')

def doctor_schedule_view(request):
    today = datetime.date.today()
    month = today.month
    year = today.year
    day = today.day
    
    

    context = {
        'today': today,
        'month': month,
        'year': year,
        'day': day,
    }
    return render(request, 'doctor/doctor-schedule.html', context)
    
def doctor_schedule_week_view(request):
    return render(request, 'doctor/doctor-schedule-week.html')

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
            return render(request, 'doctor/doctor-support.html', context) 
    else:
        return render(request, 'doctor/doctor-support.html', context)

def doctor_support_success_view(request):
    return render(request, 'doctor/doctor-support-feedback.html')

def doctor_confirm_view(request):
    return render(request, 'doctor/doctor-confirm.html')

def doctor_edit_view(request):
    user = User.objects.get(username = request.user.username)
    doctor = Health_Practitioner.objects.get(health_practitioner = user)
    instance = get_object_or_404(Health_Practitioner, health_practitioner=request.user)
    #insurance_accepted = doctor.insurance_accepted
    insurance_accepted = ast.literal_eval(doctor.insurance_accepted)
    
    if request.method == 'POST':
        form = HealthPractitionerForm(request.POST)
        if form.is_valid():
            doctor.clinics = form.cleaned_data['clinics']
            doctor.telephone = form.cleaned_data['telephone']
            doctor.specialty = form.cleaned_data['specialty']
            doctor.consultation_times = form.cleaned_data['consultation_times']
            doctor.insurance_accepted = form.cleaned_data['insurance_accepted']
            doctor.languages = form.cleaned_data['languages']
            doctor.accepting_new_patients = form.cleaned_data['accepting_new_patients']
            doctor.save()
            return redirect('doctor-edit')
        else:
            print(form.errors)
    else:
        form = HealthPractitionerForm(instance=instance)
       
    
    context = {
        'doctor': doctor,
        'form': form,
        'insurance_accepted': insurance_accepted,
    }
    return render(request, 'doctor/doctor-edit.html', context)


@login_required
def doctor_consultation_view(request, id=None):

    context = {}
    appointment_list = []

    hp = Health_Practitioner.objects.get(id=3) #(id=request.user.id)
    hp_appointments = list(Appointment.objects.filter(health_practitioner=hp).filter(app_status='PENDING').values())
    #user = User.objects.get(id=request.user.id) #id=2 for testing or id=request.user.id)
    #patient = Patient.objects.get(patient=user)
    print('HP', hp_appointments)
    print('FIRST APPT PATIENT', hp_appointments[0]['appointment_date'])
    #dataset = Appointment.objects.filter(health_practitioner=hp).filter(app_status='PENDING')
    
    for appointment in hp_appointments:

        patient = Patient.objects.get(patient_id= appointment['patient_id'])
        appt_reason = appointment['appt_reason']
        appointment_date = appointment['appointment_date']
        app_time = Appointment.TIMESLOTS[appointment['timeslots']][1]
        app_id = appointment['id']

        #user = User.objects.get(id=11) #appointment['id']) #id=2 for testing or id=request.user.id)
        appointment_data = (patient, appt_reason, appointment_date, app_time)
       
        appointment_list.append(appointment_data)
    
    
    if request.method == 'POST':

        appt = Appointment.objects.get(id=app_id)
        form = ConsultationForm(request.POST, instance=appt)
        if form.is_valid:
            app_status = form.cleaned_data['app_status']
            if app_status == "Accept":
                
                appt['app_status'] = app_status
                appt.save()

            else:
                appt.delete()

        #app_status = form
        #form = ConsultationForm(request.POST, instance=app_status)
        form.save()

    
    form = ConsultationForm(request.GET)
    
    print('APP_LIST', appointment_list)
    context = {'appointment_list': appointment_list,
               'form': form,
              }
    return render(request, 'doctor/doctor-consultations.html', context)
    
    



    #return render(request, 'doctor/doctor-edit.html', context)
