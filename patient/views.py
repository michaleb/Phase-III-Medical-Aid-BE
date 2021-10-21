from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail, get_connection
from django.db.models import Q
import ast, datetime
from django.utils.dateparse import parse_date
from django.conf import settings
from django.template.defaulttags import register
from datetime import date, timedelta
from aidApp.models import Emergency_Contact_Info, Feedback, Patient, Health_Practitioner, FAQ, Appointment, Clinic, Pharmacy, Patient_Contact_Info, Emergency_Contact_Info
from .forms import DocProfileForm, AppCreateForm#, AppUpdateForm, AppRetrieveForm 

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
    appointment = Appointment.objects.filter(Q(app_status=1)& Q(appointment_date__lt=date.today())& Q(patient=patient))
    pending_appointments = Appointment.objects.filter(Q(app_status=1)& Q(appointment_date__gte=date.today())& Q(patient=patient)).count
    
    #Select most recent appointment details to render on page
    if appointment:
        recent_date = appointment[0].appointment_date
        for app in appointment:
            if app.appointment_date >= recent_date:
                recent_date = app.appointment_date
                app_time = Appointment.TIMESLOTS[app.timeslots][1]
                app_doc = app.health_practitioner
                app_details = [recent_date, app_time, app_doc]
    
    else:
        app_details = [None]
            
    context = {
        'patient': patient,
        'prev_appointment': app_details,
        'pending_appointments': pending_appointments,
    }

    return render(request, 'patient/patient-dash.html', context)

@login_required(login_url='/users/login')
def patient_doctor_view(request):
    if request.method == "POST":
        specialty_search = request.POST.get('specialty')
        search = request.POST.get('search')

        # to prevent none value being given if user does not enter anything in the field
        if not search:
            search = specialty_search
        if not specialty_search:
            specialty_search = search

        doctors = Health_Practitioner.objects.filter(Q(health_practitioner__first_name__icontains=search) \
                  | Q(health_practitioner__last_name__icontains=search) | Q(clinics__name__icontains=search) \
                  | Q(specialty__in=(specialty_search, search)))
        
    else:
        doctors = Health_Practitioner.objects.all()
    
    context = {
        'doctors': doctors,
        
    }
    return render(request, 'patient/patient-doctor.html', context)

def patient_profile_view(request):
    user = User.objects.get(username = request.user.username)
    patient = Patient.objects.get(patient = user)
    contact = Patient_Contact_Info.objects.get(patient = patient)
    em_contact = Emergency_Contact_Info.objects.get(patient = patient)

    if request.method == 'POST':
        patient.D_O_B = request.POST.get('birthdate')
        patient.race_or_ethnicity = request.POST.get('ethnicity')
        patient.sex = request.POST.get('gender')
        patient.marital_status = request.POST.get('marital')
        patient.telephone = request.POST.get('phone')
        patient.save()
        contact.address_1 = request.POST.get('address1')
        contact.address_2 = request.POST.get('address2')
        contact.city = request.POST.get('city')
        contact.state = request.POST.get('state')
        contact.zip_code = request.POST.get('zipcode')
        contact.save()
        em_contact.name = request.POST.get('emcontactname')
        em_contact.address_1 = request.POST.get('emaddress1')
        em_contact.address_2 = request.POST.get('emaddress2')
        em_contact.city = request.POST.get('emcity')
        em_contact.state = request.POST.get('emstate')
        em_contact.zip_code = request.POST.get('emzipcode')
        em_contact.telephone = request.POST.get('emphone')
        em_contact.email = request.POST.get('ememail')
        em_contact.save()
        return redirect('patient-profile')



    context = {
        'patient': patient,
        'contact': contact,
        'em_contact': em_contact,
    }
    return render(request, 'patient/patient-profile.html', context)
    
@login_required
def DocProfile(request, id=None):

    #user = User.objects.get(id = id)
    hp = Health_Practitioner.objects.get(id=id) #health_practitioner_id=id)
    cl = Clinic.objects.filter(health_practitioner=hp)
    form = DocProfileForm()
        
    form = {'health_practitioner' : hp,
            'professional_title' : hp.professional_title,
            'professional_suffix': hp.professional_suffix,
            'telephone' : hp.telephone,
            'specialty' : hp.specialty,
            'consultation_times' : hp.consultation_times,
            'clinics' : cl,
            'insurance_accepted' : hp.insurance_accepted,
            'languages' : hp.languages,
            'accepting_new_patients' : hp.accepting_new_patients,
            'reviews': hp.reviews,
            'rating_reviews': hp.rating_reviews,
            'patient_comments': hp.patient_comments,
            }
        
    return render(request, 'patient/patient-doctor-profile.html', {'form': form})


@login_required
def CreateAppointment(request, id=None):
    
    hp = Health_Practitioner.objects.get(id=id) #health_practitioner_id=id)
    hp_email = User.objects.get(health_practitioner=hp).email
    cl = Clinic.objects.filter(health_practitioner=hp)
    user = User.objects.get(id=request.user.id) #id=2 for testing or id=request.user.id)
    patient = Patient.objects.get(patient=user)
   
    hp_appointments = list(Appointment.objects.filter(health_practitioner=hp).values())
        
    context = {}
    gform = {'health_practitioner' : hp,
            'professional_title' : hp.professional_title,
            'professional_suffix': hp.professional_suffix,
            #'telephone' : hp.telephone,
            'specialty' : hp.specialty,
            #'consultation_times' : hp.consultation_times,
            'clinics' : cl,
            'insurance_accepted' : hp.insurance_accepted,
            'languages' : hp.languages,
            'accepting_new_patients' : hp.accepting_new_patients,
            'reviews': hp.reviews,
            'rating_reviews': hp.rating_reviews,
            'patient_comments': hp.patient_comments,
            }
    
    if request.method == 'POST':
        
        form = AppCreateForm(request.POST)
        free_timeslot = True

        # check if form data is valid
        if form.is_valid():
            
            for appointment in hp_appointments:
                if appointment['appointment_date'] == form.cleaned_data['appointment_date']:
                    if appointment['timeslots'] == form.cleaned_data['timeslots']:
                        free_timeslot = False
                            
            app_date = form.cleaned_data['appointment_date']
            timeslot= form.cleaned_data['timeslots']
            app_reason = form.cleaned_data['appt_reason']
                        
            # check if date is valid and timeslot unbooked
            if free_timeslot and app_date > date.today()- timedelta(days=1): 
                appointment = Appointment.objects.create(health_practitioner=hp,
                                                        patient=patient, 
                                                        appointment_date= app_date,
                                                        timeslots = timeslot, 
                                                        appt_reason=app_reason,
                                                        app_status=0)
                appointment.save()
                hp.appointments_pending = hp.appointments_pending +1
                hp.save()

                appointment_email = app_reason+" "+ str(app_date) 
                            
                con = get_connection('django.core.mail.backends.console.EmailBackend')
                send_mail('Appointment request',
                        appointment_email,
                        None,
                        [hp_email],
                        connection=con            
                )
                            
                messages.success(request, "Your appointment request was submitted successfully! Thank you.")
                
            else:
                messages.error(request, "Your chosen appointment date and/or time is unavailable.")
                #return redirect('patient-appt', id=id)
                
        else:
            context = {'gform': gform,
                       'form': form,
                      }    
            return render(request,'patient/patient-appt.html',context)        


    form = AppCreateForm(request.GET)
        
    form = {'appt_reason': form['appt_reason'],
            'timeslots': form['timeslots'],
            'appointment_date': form['appointment_date'],
            }
            
    context = {'gform': gform,
               'form': form,
              }    
    return render(request, 'patient/patient-appt.html', context)
    

# def patient_profile_view(request):

#     return render(request, 'patient/patient-profile.html')


        
def patient_clinic_view(request):
    if request.method == "POST":
        search = request.POST.get('search')
        if request.POST.get('clinic-pharmacy') == 'clinics':
            query = Clinic.objects.filter(name__icontains=search)
        elif request.POST.get('clinic-pharmacy') == 'pharmacies':
            query = Pharmacy.objects.filter(name__icontains=search)
        category = request.POST.get('clinic-pharmacy')
    else:
        query = Pharmacy.objects.all()
        category = 'pharmacies'
    
    context = {

        'query': query,
        'category': category,

    }
    
    return render(request, 'patient/patient-clinic.html', context)

def clinic_info_view(request, category, pk):
    
    if category == 'pharmacies':
        location = get_object_or_404(Pharmacy, id=pk)
    else:
        location = get_object_or_404(Clinic, id=pk)

    context = {

        'location': location,
   
     }

    return render(request, 'patient/patient-clinic-info.html', context)