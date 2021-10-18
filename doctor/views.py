from django.db.models.query import EmptyQuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
import datetime, ast
from datetime import date
from aidApp.models import Emergency_Contact_Info, Feedback, Medical_History, Patient, Health_Practitioner, Clinic, Appointment, Patient_Contact_Info
from .forms import ConsultationForm, HealthPractitionerForm


# Create your views here.

@login_required
def doctor_dash_view(request):
    user = User.objects.get(username = request.user.username)
    doctor = Health_Practitioner.objects.get(health_practitioner = user)
    pending_appointments = Appointment.objects.filter(Q(app_status=1)& Q(appointment_date__gte=date.today())& Q(health_practitioner=doctor))

    #Select next scheduled appointment details to render on page
    if pending_appointments:
        next_app_date = pending_appointments[0].appointment_date
        for app in pending_appointments:
            if app.appointment_date <= next_app_date:
                next_app_date = app.appointment_date
                app_time = Appointment.TIMESLOTS[app.timeslots][1]
                app_patient = app.patient
                app_details = [next_app_date, app_time, app_patient]
    
    else:
        app_details = [None]
    
    context = {
        'doctor': doctor,
        'pending_appointments': app_details,
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


def doctor_confirm_view(request, id=None):

    if request.method == "POST":
        
        appt = Appointment.objects.get(id=id)
        appt.app_status = request.POST.get("app_status")
        appt.save()
        
        if appt.app_status == "1":
            #appt.save()
            messages.success(request, "Appointment has been added to your schedule")
            #return redirect('doctor-consultations')
        else:
            #appt.delete()
            messages.error(request, "Appointment has been removed from your schedule")
            #return redirect('doctor-consultations')
    
    
    
    form = ConsultationForm(request.GET)
    context = {}

    hp_user = User.objects.get(id=request.user.id)
    hp = Health_Practitioner.objects.get(health_practitioner=hp_user)    
    patient = Appointment.objects.get(id=id).patient
    user = User.objects.get(patient=patient)
    patient_contact = Patient_Contact_Info.objects.get(patient=patient)
    recent_visit = Appointment.objects.filter(Q(health_practitioner=hp)& Q(patient=patient)& Q(app_status=1)& Q(appointment_date__lt=date.today()))
    
    try:
        patient_econtact = Emergency_Contact_Info.objects.get(patient=patient)
    except:
        patient_econtact = None
            
    try:
        medical_records = Medical_History.objects.get(patient=patient)
    except:
        medical_records = None
    
    finally:
        context = {'patient': patient,
                   'patient_contact': patient_contact,
                   'patient_econtact': patient_econtact, 
                   'recent_visit': recent_visit,
                   'medical_records': medical_records,
                   'form': form,
                   'user': user,
                  }


    return render(request, 'doctor/doctor-confirm.html', context)

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
def doctor_consultation_view(request):

    context = {}
    
    user = User.objects.get(id=request.user.id)
    hp = Health_Practitioner.objects.get(health_practitioner=user)
    appointments = Appointment.objects.filter(Q(health_practitioner=hp) & Q(app_status=0) & Q(appointment_date__gte=date.today()))
    prev_appointments = Appointment.objects.filter(Q(health_practitioner=hp) & Q(appointment_date__lt=date.today()))
        
    if request.method == 'POST':
                
        id = request.POST.get("appointment.id")
        appt = Appointment.objects.get(id=id)
        appt.app_status = request.POST.get("app_status")
        appt.save()

        messages.success(request, "Appointment has been added to your schedule")
        #return redirect('doctor-consultations')

    form = ConsultationForm(request.GET)
    
    context = {'appointments': appointments,
               'prev_appointments': prev_appointments, 
               'form': form,
              }
    return render(request, 'doctor/doctor-consultations.html', context)
    