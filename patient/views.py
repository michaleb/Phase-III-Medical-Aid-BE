from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail, get_connection
from django.db.models import Q
from django.conf import settings
from django.template.defaulttags import register
from datetime import date, timedelta
from aidApp.models import Feedback, Patient, Health_Practitioner, FAQ, Appointment, Clinic
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

    return render(request, 'patient/patient-dash.html')

def patient_doctor_view(request):
    
    context = {
        'doctors': Health_Practitioner.objects.all(),
        
    }
    return render(request, 'patient/patient-doctor.html', context)


@login_required
def DocProfile(request, id=None):

    #user = User.objects.get(id = id)
    hp = Health_Practitioner.objects.get(health_practitioner_id=id)
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
    
    #if "user" in request.session: 
        
    hp = Health_Practitioner.objects.get(health_practitioner_id=id)
    hp_email = User.objects.get(health_practitioner=hp).email
    cl = Clinic.objects.filter(health_practitioner=hp)
    user = User.objects.get(id=request.user) #id=2 for testing or id=request.user)
    patient = Patient.objects.get(patient=user)
   
    hp_appointments = list(Appointment.objects.filter(health_practitioner=hp).values())
    #print('HP',hp_appointments)
    
    # List of dates with 'approved' appointments and dictionary of dates with unavailable timeslots  
    dateList = []
    dateDict = {}   
    for appointment in hp_appointments:
        t = appointment['timeslots']
        days = (appointment['appointment_date']).strftime('%Y-%m-%d')
        if appointment['app_status'] == 'PENDING':

            if days not in dateList:
                dateList.append(days)
                dateDict[days] = [t]
                        
            else:
                dateDict[days].append(t) 

    
    #print('dateDict', dateDict)
    
    #Create a function that returns booked timeslots for a given date
    def Booked_slots(datelist, app_date):
        booked_timeslots = []
        for key in datelist:
            if key == str(app_date):
                for timeslot in datelist[key]:
                    booked_timeslots.append(timeslot)
        return booked_timeslots

    form = {}
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
        # check if form data is valid
                
        if form.is_valid() and form.cleaned_data['appointment_date'] > date.today()- timedelta(days=1): 
            app_date = form.cleaned_data['appointment_date']
            timeslot= form.cleaned_data['timeslots']
            app_reason = form.cleaned_data['appt_reason']

            appointment = Appointment.objects.create(health_practitioner=hp,
                                                    patient=patient, 
                                                    appointment_date= app_date,
                                                    timeslots = timeslot, 
                                                    appt_reason=app_reason,
                                                    app_status="PENDING")
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
            context = {'gform': gform,
                        'form': form,
                      }    
            
            return render(request,'patient/patient-appt.html',context)

    
    else:
        form = AppCreateForm(request.GET)
        
        #print('BOOKED', Booked_slots(dateDict, date.today()))
        form = {'appt_reason': form['appt_reason'],
                'timeslots': form['timeslots'],
                'appointment_date': form['appointment_date'],
                'booked_timeslots': Booked_slots(dateDict, date.today()),
               }
               
        context = {'gform': gform,
                   'form': form,
                  }    
        return render(request, 'patient/patient-appt.html', context)
    
    
    context = {'gform': gform,
              }    
    return render(request, 'patient/patient-appt.html', context)           
