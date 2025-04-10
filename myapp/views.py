from django.contrib.auth import logout
from django.db import IntegrityError
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .models import Farmer, Cattle, Vet
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.db.models import Q
from datetime import date, timedelta
from django.db.models.signals import post_save
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.base import TemplateView
from django.core.mail import EmailMessage, message
from django.conf import settings
from django.contrib import messages
from myapp.models import Appointment,VACCINATION_SCHEDULES
from django.views.generic import ListView
from datetime import datetime, date, timedelta  # Correct import

from django.template import Context
from django.template.loader import render_to_string, get_template
import pandas as pd
from django.http import HttpResponse
from .models import Cattle
import io
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from .forms import SignUpForm, LoginForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.
def index(request):
    num_users = Farmer.objects.count()
    num_cattles = Cattle.objects.count()
    num_reg = Vaccination_Reg.objects.count()
    # Pass the num_users variable to your template context
    context = {'num_users': num_users, 'num_cattles': num_cattles, 'num_reg': num_reg}
    return render(request,"index.html", context)

def about(request):
    num_users = Farmer.objects.count()
    num_cattles=Cattle.objects.count()
    num_reg=Vaccination_Reg.objects.count()
    # Pass the num_users variable to your template context
    context = {'num_users': num_users,'num_cattles': num_cattles,'num_reg':num_reg}
    return render(request, 'about.html', context)


def reg(request):
    msg = None
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user with role flags
            
            # Now create the corresponding role-specific record
            if user.is_farmer:
                # Check if a farmer with this email already exists
                try:
                    # Try to get existing farmer
                    farmer = Farmer.objects.get(email=user.email)
                    # If exists, update the user field
                    farmer.user = user
                    farmer.save()
                except Farmer.DoesNotExist:
                    # Create new farmer record
                    farmer = Farmer(
                        user=user,
                        name=user.username,
                        email=user.email,
                        phone="0000000000"  # Default
                    )
                    farmer.save()
                
            elif user.is_vet:
                # Check if a vet with this email already exists
                try:
                    # Try to get existing vet
                    vet = Vet.objects.get(email=user.email)
                    # If exists, update the user field
                    vet.user = user
                    vet.save()
                except Vet.DoesNotExist:
                    # Create new vet record
                    vet = Vet(
                        user=user,
                        name=user.username,
                        email=user.email,
                        phone="0000000000"  # Default
                    )
                    vet.save()
                
            msg = 'user created'
            return redirect('login2')
        else:
            msg = 'form is not valid'
    else:
        form = SignUpForm()
    return render(request,'register.html', {'form': form, 'msg': msg})

def sign(request):
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_admin:
                login(request, user)
                request.session['firstname'] = user.first_name  # Set session variable
                return redirect('adminpage')
            elif user is not None and user.is_farmer:
                login(request, user)
                request.session['firstname'] = user.first_name  # Set session variable
                return redirect('farmer')
            elif user is not None and user.is_vet:
                login(request, user)
                request.session['firstname'] = user.first_name  # Set session variable
                return redirect('cattle_registration')
            else:
                msg = 'invalid credentials'
        else:
            msg = 'error validating form'
    return render(request, 'login2.html', {'form': form, 'msg': msg})





def farmer(request):
    return render(request,'farmer.html')


def vet(request):
    return render(request,'vet.html')


def sms(request):
    return render(request,'sms.html' )

def dashboard(request):
    return render(request,'index3.html' )

def service(request):
    return render(request,"service.html")








from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Cattle
from .utils import generate_cattle_report

from django.shortcuts import get_object_or_404
from django.conf import settings
import os

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Cattle, Farmer
from datetime import date

def cattlereg(request):
    """
    Handle cattle registration form submission
    """
    if request.method == 'POST':
        try:
            # Extract form data
            tagno = request.POST.get('tagno')
            breed = request.POST.get('breed')
            gender = request.POST.get('gender')
            dob = request.POST.get('dob')
            age_months = request.POST.get('age_months')
            age_years = request.POST.get('age_years')
            weight = request.POST.get('weight')
            color = request.POST.get('color')

            # Log the form data for debugging
            print(f"Form Data: tagno={tagno}, breed={breed}, gender={gender}, dob={dob}, age_months={age_months}, age_years={age_years},"
                  f"weight={weight}, color={color}")

            # Validate required fields
            if not all([tagno, breed, gender, dob, age_months, age_years, weight, color]):
                messages.error(request, 'All fields are required.')
                return render(request, 'farmer.html', {'form_data': request.POST})

            # Check if tag number already exists
            if Cattle.objects.filter(tagno=tagno).exists():
                messages.error(request, f'A cattle record with tag number {tagno} already exists.')
                return render(request, 'farmer.html', {'form_data': request.POST})

            # Convert date of birth
            dob = date.fromisoformat(dob)
            
            # Calculate age
            today = date.today()
            age_months = (today.year - dob.year) * 12 + (today.month - dob.month)
            age_years = age_months // 12

            # Retrieve the owner (this should be replaced with actual logic to get the current farmer)
            owner = Farmer.objects.get(id=1)  # Replace 1 with the actual owner ID or logic to get the current user

            # Create cattle record
            cattle = Cattle.objects.create(
                tagno=tagno,
                breed=breed,
                gender=gender,
                dob=dob,
                age_months=age_months,
                age_years=age_years,
                color=color,
                weight=float(weight),
                owner=owner  # Set the owner field
            )

            # Success message
            messages.success(request, f'Cattle with tag number {tagno} registered successfully!')
            
            # Redirect or render
            return redirect('cattle_nutrition', cattle_id=cattle.id)


        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'farmer.html', {'form_data': request.POST})

    # GET request render
    return render(request, 'farmer.html', {'form_data': {}})
from django.contrib import messages
from .models import CattleRecord
from datetime import date
from django.shortcuts import render, redirect
from django.http import JsonResponse

# Add this new view function to handle the AJAX request
def get_cattle_data(request, tagno):
    try:
        cattle = Cattle.objects.get(tagno=tagno)
        data = {
            'tagno': cattle.tagno,
            'breed': cattle.breed,
            'gender': cattle.gender,
            'dob': cattle.dob.isoformat(),  # Format date as YYYY-MM-DD
            'age_months': cattle.age_months,
            'age_years': cattle.age_years,
            'weight': cattle.weight,
            'color': cattle.color
        }
        return JsonResponse(data)
    except Cattle.DoesNotExist:
        return JsonResponse({'error': 'Cattle not found'}, status=404)

# Update your cattle_registration view to pass all cattle to the template
def cattle_registration(request):
    if request.method == 'POST':
        try:
            # Extract form data
            tagno = request.POST.get('tagno')
            breed = request.POST.get('breed')
            gender = request.POST.get('gender')
            date_of_birth = request.POST.get('dob')
            vaccination_type = request.POST.get('vaccinationType')
            last_vaccination_date = request.POST.get('last_vaccination_date')
            observation = request.POST.get('observation')
            disease_diagnosis = request.POST.get('disease')
            weight = request.POST.get('weight')
            color = request.POST.get('color')

            # Ensure dates are properly parsed to date objects
            dob = date.fromisoformat(date_of_birth)
            last_vacc_date = date.fromisoformat(last_vaccination_date)
            
            # Create your cattle record
            cattle = Cattle.objects.get(tagno=tagno)
            cattle_record = CattleRecord(
                tagno=cattle,
                breed=breed,
                gender=gender,
                dob=dob,
                vaccination_type=vaccination_type,
                last_vaccination_date=last_vacc_date,
                age_months=cattle.age_months,
                age_years=cattle.age_years,
                observation=observation,
                disease_diagnosis=disease_diagnosis,
                weight=float(weight),
                color=color
            )
            cattle_record.save()

            messages.success(request, f'Cattle with tag number {tagno} registered successfully!')
            return render(request, 'vet.html', {
                'cattle_record': cattle_record,
                'all_cattle': Cattle.objects.all()
            })

        except Exception as e:
            print(f"Error details: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'vet.html', {'all_cattle': Cattle.objects.all()})

    # For GET requests
    all_cattle = Cattle.objects.all()
    return render(request, 'vet.html', {'all_cattle': all_cattle})

from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date
from .models import Vet, Appointment


    
    #
import os
from django.conf import settings
from django.http import HttpResponse, Http404

def download_report(request, tagno):
    reports_dir = os.path.join(settings.BASE_DIR, 'reports')
    filepath = os.path.join(reports_dir, f'cattle_{tagno}.pdf')

    if not os.path.exists(filepath):
        raise Http404("Report not found. Please register the cattle again.")

    with open(filepath, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="cattle_{tagno}.pdf"'
        return response


from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import date
from .models import Cattle  # We'll create this model

def calculate_age(dob):
    """
    Calculate age in months and years based on date of birth
    """
    today = date.today()
    age_months = (today.year - dob.year) * 12 + (today.month - dob.month)
    age_years = age_months // 12
    return age_months, age_years





# Generate Excel Report

def download_cattle_excel(request):
    # Query cattle data
    cattle_data = Cattle.objects.all().values()
    df = pd.DataFrame(list(cattle_data))

    # Create a BytesIO buffer
    buffer = io.BytesIO()

    # Write the dataframe to the buffer
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='CattleData')

    # Set the buffer position to the beginning
    buffer.seek(0)

    # Create the HTTP response
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=cattle_data.xlsx'
    return response

# Generate PDF Report
def download_cattle_pdf(request):
    # Query cattle data
    cattle_data = Cattle.objects.all()
    html_string = render_to_string('cattle_pdf.html', {'cattle_data': cattle_data})

    # Create a BytesIO buffer
    buffer = io.BytesIO()

    # Create the PDF object, and write the HTML string to it
    pisa.CreatePDF(io.StringIO(html_string), dest=buffer)

    # Set the buffer position to the beginning
    buffer.seek(0)

    # Create the HTTP response
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=cattle_data.pdf'
    return response

def test(request):
    return render(request, "404.html")
def profile(request):
    username = request.session.get('username')
    if not username:
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('/login2/')
    farmer_id = request.session.get('id')
    farmer = Farmer.objects.get(id=farmer_id)
    cattles = Cattle.objects.filter(owner=farmer)

    return render(request, "profile.html", {'farmer': farmer, 'cattles': cattles})
def logout_view(request):
    logout(request)
    return redirect('index')
def vaccinate(request):
    username = request.session.get('username')
    if not username:
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('/login2/')
    username = request.session.get('id')
    cattles = Cattle.objects.filter(owner=username)
    vaccines = Vaccines.objects.all()
    diseases = Disease.objects.all()
    context = {'cattles': cattles, 'diseases': diseases, 'vaccines': vaccines}
    return render(request, 'vaccinate.html', context)

def view_vaccine(request, id):
    username = request.session.get('username')
    if not username:
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('/login2/')
    # Get the cattle object for the given id
    cattle = Cattle.objects.get(id=id)

    # Store the cattle's id in the session
    request.session['cattleid'] = cattle.id

    # Get the cattle's age
    age = cattle.age
    tagno=cattle.tagno

    # Get all the vaccination registrations for the cattle
    vaccination_registrations = Vaccination_Reg.objects.filter(cattleid=cattle)

    # Get a list of diseases for which the cattle has already been vaccinated
    vaccinated_diseases = [vr.diseaseid for vr in vaccination_registrations]

    # Get the vaccination status for each disease for the cattle
    vaccination_statuses = {}
    vaccination_statuses_query = Vaccination_S.objects.filter(cattleid=cattle)
    for vs in vaccination_statuses_query:
        disease_id = vs.diseaseid.id
        if vs.firstdose_status and vs.seconddose_status:
            vaccination_statuses[disease_id] = 2
        elif vs.firstdose_status:
            vaccination_statuses[disease_id] = 1
        else:
            vaccination_statuses[disease_id] = 0

    # Get a list of diseases for which the cattle is eligible for the first dose
    eligible_for_first_dose = Disease.objects.filter(firstdose__lte=age).exclude(disease__in=vaccinated_diseases)

    # Get a list of diseases for which the cattle is eligible for the second dose
    eligible_for_second_dose = []
    for disease in vaccinated_diseases:
        if disease.id in vaccination_statuses and vaccination_statuses[disease.id] == 1:
            eligible_for_second_dose_query = Disease.objects.filter(id=disease.id, boosterdose__gte=age)
            if eligible_for_second_dose_query.exists():
                # Check if the cattle has already received the second dose or if it has already been requested
                if Vaccination_Reg.objects.filter(cattleid=cattle, diseaseid=disease, dose=2).exists() or \
                        Vaccination_Reg.objects.filter(cattleid=cattle, diseaseid=disease, dose=1,
                                                       status=False).exists():
                    continue
                eligible_for_second_dose.append(eligible_for_second_dose_query.first())

    # Get a list of cattle eligible for yearly dose
    eligible_for_yearly_dose = []
    fourth_dose_diseases = [vr.diseaseid for vr in vaccination_registrations if vr.dose == 4]
    vaccination_statuses_query = Vaccination_S.objects.filter(cattleid=cattle)
    for vs in vaccination_statuses_query:
        if vs.eligibility_yd and vs.ldate_approved is not None:
            today = date.today()
            if today >= vs.ldate_approved + timedelta(days=365):
                if vs.diseaseid not in fourth_dose_diseases:
                    eligible_for_yearly_dose.append({
                        'id': vs.diseaseid.id,
                        'disease': vs.diseaseid.disease,
                        'vaccine': vs.diseaseid.vaccine,
                        'last_vaccination_date': vs.ldate_approved,
                    })

    # Get all the available vaccines
    vaccines = Vaccines.objects.all()


    context = {
        'cattle': cattle,
        'tagno': tagno,
        'eligible_for_first_dose': eligible_for_first_dose,
        'eligible_for_second_dose': eligible_for_second_dose,
        'vaccination_statuses': vaccination_statuses,
        'eligible_for_yearly_dose': eligible_for_yearly_dose,
        'vaccines': vaccines,
    }


    # Pass the relevant data to the template for rendering
    return render(request, 'vaccinate1.html', context)

def booking(request, disease_id):
    disease = Disease.objects.get(id=disease_id)
    dis = disease.disease
    vac = disease.vaccine
    farmer_id = request.session.get('id')
    farmer = Farmer.objects.filter(id=farmer_id).first()
    farmer_name = f"{farmer.firstname} {farmer.lastname}"
    cattle = Cattle.objects.get(id=request.session.get('cattleid'))
    tagno = cattle.tagno

    # Check if booking for first or second dose
    vaccination_registrations = Vaccination_Reg.objects.filter(cattleid=cattle, diseaseid=disease)
    if vaccination_registrations.exists():
        # Already registered for the first dose
        dose = 2 if vaccination_registrations.first().dose == 1 else 1

        # Check if eligible for second dose
        first_dose_date_approved = vaccination_registrations.first().date_approved
        six_months_from_first_dose = first_dose_date_approved + timedelta(days=180)
        if dose == 2 and date.today() < six_months_from_first_dose:
            # Not eligible for second dose yet
            messages.error(request, 'Not Eligible for Second Dose Yet.')
            return HttpResponseRedirect(f'/viewv/{cattle.id}/')
    else:
        # First time registration for the disease, set dose as 0
        dose = 0

    # Create a new Vaccination_Reg object
    sa = Vaccination_Reg(cattleid=cattle, cattletagno=tagno, farmerid=farmer, farmer_name=farmer_name,
                                      diseaseid=disease, disease=dis, vaccine=vac, date_requested=date.today(),
                                      dose=dose, status=False)
    sa.save()

    cattles = Cattle.objects.filter(owner=farmer_id)
    vaccines = Vaccines.objects.all()
    diseases = Disease.objects.all()
    context = {'cattles': cattles, 'diseases': diseases, 'vaccines': vaccines}
    return HttpResponseRedirect(f'/viewv/{cattle.id}/')



def booking2(request, disease_id):
    disease = Disease.objects.get(id=disease_id)
    dis = disease.disease
    vac = disease.vaccine
    farmer_id = request.session.get('id')
    farmer = Farmer.objects.filter(id=farmer_id).first()
    farmer_name = f"{farmer.firstname} {farmer.lastname}"
    cattle = Cattle.objects.get(id=request.session.get('cattleid'))
    tagno = cattle.tagno
    dose = 4

    # Create a new Vaccination_Reg object
    sa = Vaccination_Reg(cattleid=cattle, cattletagno=tagno, farmerid=farmer, farmer_name=farmer_name,
                                      diseaseid=disease, disease=dis, vaccine=vac, date_requested=date.today(),
                                      dose=dose, status=False)
    sa.save()

    cattles = Cattle.objects.filter(owner=farmer_id)
    vaccines = Vaccines.objects.all()
    diseases = Disease.objects.all()
    context = {'cattles': cattles, 'diseases': diseases, 'vaccines': vaccines}
    return HttpResponseRedirect(f'/viewv/{cattle.id}/')



def vaccination_history(request):
    username = request.session.get('username')
    if not username:
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('/login2/')
    farmer_id = request.session.get('id')
    farmer = Farmer.objects.get(id=farmer_id)
    cattles = Cattle.objects.filter(owner=farmer_id)
    vaccination_data = []
    ai_data = []
    for cattle in cattles:
        cattle_vaccinations = Vaccination_Reg.objects.filter(cattleid=cattle)
        vaccination_data.append({'cattle': cattle, 'vaccinations': cattle_vaccinations})
    for cattle in cattles:
        cattle_ai = ArtificialInsemination.objects.filter(cattleid=cattle)
        ai_data.append({'cattle': cattle, 'artificialinsemination': cattle_ai})
    return render(request, 'History.html', {'vaccination_data': vaccination_data, 'ai_data': ai_data, 'farmer': farmer})



def changepassword(request):
    if request.method == "POST":
        email = request.POST.get("email")
        newpass = request.POST.get("t2")
        confrmpass = request.POST.get("t3")

        try:
            farmer = Farmer.objects.get(email=email)
        except Farmer.DoesNotExist:
            return render(request, "chpswd.html")

        if newpass == confrmpass:
            farmer.password = newpass
            farmer.save()
            return render(request, 'index.html')
        else:
            return render(request, "chpswd.html")

    return render(request, "chpswd.html")






from datetime import date, timedelta

def ai(request):
    username = request.session.get('username')
    if not username:
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('/login2/')
    username = request.session.get('id')
    cattles = Cattle.objects.filter(owner=username, gender='Female', age__gte=12)
    vaccines = Vaccines.objects.all()
    diseases = Disease.objects.all()

    # filter cattles by pregnant_status and time since date_approved
    filtered_cattles = []
    for cattle in cattles:
        ai_records = ArtificialInsemination.objects.filter(cattleid=cattle)
        if ai_records:
            last_ai_record = ai_records.latest('date_approved')
            if last_ai_record.pregnant_status is False:
                filtered_cattles.append(cattle)
            elif last_ai_record.pregnant_status is True and last_ai_record.date_approved + timedelta(days=365) <= date.today():
                filtered_cattles.append(cattle)
        else:
            filtered_cattles.append(cattle)

    context = {'cattles': filtered_cattles, 'diseases': diseases, 'vaccines': vaccines}
    return render(request, 'ai.html', context)


def book_ai(request, cattle_id):
    farmer_id = request.session.get('id')
    ai = ArtificialInsemination.objects.create(
        cattleid_id=cattle_id,
        farmerid_id=farmer_id,
        date_requested=date.today(),
    )
    ai.save()
    return HttpResponseRedirect('/ai/')

def update_pregnancy_status(request, ai_id):
    ai = ArtificialInsemination.objects.get(id=ai_id)
    if request.method == 'POST' and ai.pregnant_status is None:
        pregnancy_status = request.POST.get('pregnancy_status')
        if pregnancy_status == 'True':
            ai.pregnant_status = True
        elif pregnancy_status == 'False':
            ai.pregnant_status = False
        ai.save()
    return redirect('/vaccination-history/')

def delete_cattle(request, cattle_id):
    cattle = get_object_or_404(Cattle, id=cattle_id)
    if request.method == 'POST':
        cattle.delete()
        return redirect('/profile/')








class HomeTemplateView(TemplateView):
    template_name = "index2.html"
    
    def post(self, request):
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        email = EmailMessage(
            subject= f"{name} from doctor family.",
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=[settings.EMAIL_HOST_USER],
            reply_to=[email]
        )
        email.send()
        return HttpResponse("Email sent successfully!")


from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Appointment, Vet
from datetime import datetime, date
from django.utils import timezone


class AppointmentTemplateView(TemplateView):
    template_name = 'appointment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use the get_user_model approach
        context['vets'] = User.objects.filter(is_vet=True)
        return context
    
    def post(self, request, *args, **kwargs):
        vet_id = request.POST.get('vet_id')
        try:
            vet = User.objects.get(id=vet_id, is_vet=True)
            appointment = Appointment(
                vet=vet,
                fname=request.POST.get('fname'),
                lname=request.POST.get('lname'),
                email=request.POST.get('email'),
                mobile=request.POST.get('mobile'),
                request_details=request.POST.get('request')
            )
            appointment.save()
            messages.success(request, "Appointment request submitted successfully!")
            return redirect('farmer')
        except User.DoesNotExist:
            messages.error(request, "Selected veterinarian does not exist.")
            context = self.get_context_data()
            return render(request, self.template_name, context)
from django.contrib.auth.mixins import LoginRequiredMixin
class ManageAppointmentTemplateView(LoginRequiredMixin, ListView):
    template_name = "manage-appointments.html"
    model = Appointment
    context_object_name = "appointments"
    paginate_by = 3

    def get_queryset(self):
        # Ensure the logged-in user is a vet
        if self.request.user.is_vet:
            # Filter appointments where the 'vet' field matches the logged-in user
            return Appointment.objects.filter(vet=self.request.user)
        else:
            # Optionally handle cases where a non-vet user accesses this view
            return Appointment.objects.none()  # Or redirect/display an error

    def post(self, request):
        date = request.POST.get("date")
        appointment_id = request.POST.get("appointment-id")
        appointment = Appointment.objects.get(id=appointment_id)
        appointment.accepted = True
        appointment.accepted_date = datetime.now()
        appointment.appointment_date = date
        appointment.save()

        data = {
            "fname": appointment.fname,
            "date": date,
        }

        message = get_template('email.html').render(data)
        email = EmailMessage(
            "About your appointment",
            message,
            settings.EMAIL_HOST_USER,
            [appointment.email],
        )
        email.content_subtype = "html"
        email.send()

        messages.add_message(request, messages.SUCCESS, f"You accepted the appointment of {appointment.fname}")
        return HttpResponseRedirect(request.path)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({
            "title": "Manage Appointments"
        })
        return context






from django.contrib.auth import logout
from django.db import IntegrityError
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .models import Farmer, Cattle, Appointment, Vaccination
from datetime import date, timedelta, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.views.generic.base import TemplateView
from django.core.mail import EmailMessage
from django.conf import settings
from django.views.generic import ListView
from django.template.loader import get_template
import pandas as pd
import io
# from xhtml2pdf import pisa
from myapp.decorators import role_required

# Create your views here.
def index(request):
    num_users = Farmer.objects.count()
    num_cattles = Cattle.objects.count()
    context = {'num_users': num_users, 'num_cattles': num_cattles}
    return render(request, "index.html", context)

def about(request):
    num_users = Farmer.objects.count()
    num_cattles = Cattle.objects.count()
    context = {'num_users': num_users, 'num_cattles': num_cattles}
    return render(request, 'about.html', context)



def service(request):
    return render(request, "service.html")




def download_cattle_excel(request):
    cattle_data = Cattle.objects.all().values()
    df = pd.DataFrame(list(cattle_data))
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='CattleData')
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=cattle_data.xlsx'
    return response

def download_cattle_pdf(request):
    cattle_data = Cattle.objects.all()
    html_string = render_to_string('cattle_pdf.html', {'cattle_data': cattle_data})
    buffer = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html_string), dest=buffer)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=cattle_data.pdf'
    return response

def test(request):
    return render(request, "404.html")

def profile(request):
    username = request.session.get('username')
    if not username:
        messages.error(request, 'You must be logged in to access this page.')
        return redirect('/login2/')
    farmer_id = request.session.get('id')
    farmer = Farmer.objects.get(id=farmer_id)
    cattles = Cattle.objects.filter(owner=farmer)
    return render(request, "profile.html", {'farmer': farmer, 'cattles': cattles})

def logout_view(request):
    logout(request)
    return redirect('index')



def changepassword(request):
    if request.method == "POST":
        email = request.POST.get("email")
        newpass = request.POST.get("t2")
        confrmpass = request.POST.get("t3")
        try:
            farmer = Farmer.objects.get(email=email)
        except Farmer.DoesNotExist:
            return render(request, "chpswd.html")
        if newpass == confrmpass:
            farmer.password = newpass
            farmer.save()
            return render(request, 'index.html')
        else:
            return render(request, "chpswd.html")
    return render(request, "chpswd.html")





def delete_cattle(request, cattle_id):
    cattle = get_object_or_404(Cattle, id=cattle_id)
    if request.method == 'POST':
        cattle.delete()
        return redirect('/profile/')
    


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Cattle, CattleProductionStage
from .utils import fetch_nutrition_from_api, get_feeding_tips
import json
from django.contrib import messages

@login_required
def cattle_nutrition(request, cattle_id):
    # Get the cattle with verification that it belongs to the logged-in farmer
    cattle = get_object_or_404(Cattle, id=cattle_id)
    
    # Get or create a production stage record for this cattle
    production_stage, created = CattleProductionStage.objects.get_or_create(
        cattle=cattle,
        defaults={'stage': 'calf' if cattle.age_months <= 6 else 'heifer' if cattle.age_months <= 24 else 'dry'}
    )
    
    # Handle form submission to update production stage and milk production
    if request.method == "POST":
        new_stage = request.POST.get('stage')
        new_milk_production = request.POST.get('milk_production') or None
        
        if new_stage:
            production_stage.stage = new_stage
        
        if new_milk_production:
            production_stage.milk_production = float(new_milk_production)
        
        production_stage.save()
        messages.success(request, "Production information updated successfully.")
        return redirect('cattle_nutrition', cattle_id=cattle_id)
    
    # Get nutrition data
    nutrition_data = fetch_nutrition_from_api(cattle, production_stage)
    
    # Get feeding tips
    feeding_tips = get_feeding_tips(cattle, production_stage)
    
    context = {
        'cattle': cattle,
        'production_stage': production_stage,
        'nutrition_data': nutrition_data,
        'feeding_tips': feeding_tips,
        'local_resources': get_local_resources()
    }
    
    return render(request, 'cattle_nutrition.html', context)

def get_local_resources():
    """Returns a list of local agricultural extension resources"""
    return [
        {
            'name': 'Local Agricultural Extension Office',
            'description': 'Contact your local office for personalized advice',
            'contact': 'Call your district agriculture office'
        },
        {
            'name': 'Dairy Farming WhatsApp Groups',
            'description': 'Join local dairy farming groups to share knowledge',
            'contact': 'Ask other farmers for group links'
        },
        {
            'name': 'Veterinary Services',
            'description': 'Regular check-ups can prevent nutritional issues',
            'contact': 'Find local vets through your agricultural office'
        }
    ]


from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
# import xlsxwriter
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
# Assuming you have a model for cattle records
from .models import CattleRecord
from django.http import JsonResponse
from django.db.models import Count, F, ExpressionWrapper, DateField, IntegerField, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json

def vaccination_dashboard(request):
    """View function for vaccination dashboard page"""
    return render(request, 'cattle_vaccination_dashboard.html')

def get_vaccination_data(request):
    # Extract filter parameters
    vaccine_type = request.GET.get('vaccine_type', 'all')
    period = request.GET.get('period', 'all')
    
    # Base queryset
    queryset = CattleRecord.objects.all()
    
    # Apply vaccine type filter
    if vaccine_type != 'all':
        queryset = queryset.filter(vaccination_type=vaccine_type)
    
    # Apply time period filter
    if period != 'all':
        months = int(period)
        start_date = timezone.now() - timedelta(days=months*30)
        queryset = queryset.filter(last_vaccination_date__gte=start_date)
    
    # Get counts for dashboard stats
    total_cattle = Cattle.objects.count()
    
    # Since there's no is_vaccinated field, count those with a vaccination date
    vaccinated_cattle = queryset.filter(last_vaccination_date__isnull=False).count()
    
    due_cattle = queryset.filter(
        next_vaccination_due__lte=timezone.now().date()
    ).count()
    
    vaccination_rate = 0
    if total_cattle > 0:
        vaccination_rate = round((vaccinated_cattle / total_cattle) * 100)
    
    # Get vaccine type distribution
    vaccine_distribution = queryset.filter(
        last_vaccination_date__isnull=False
    ).values('vaccination_type').annotate(
        count=Count('vaccination_type')
    ).order_by('vaccination_type')
    
    vaccine_data = {}
    for item in vaccine_distribution:
        if item['vaccination_type']:  # Ensure we have a valid type
            vaccine_data[item['vaccination_type']] = item['count']
    
    # Get cattle due for vaccination
    due_cattle_records = queryset.filter(
        next_vaccination_due__lte=timezone.now().date()
    ).select_related('tagno').order_by('next_vaccination_due')
    
    due_cattle_list = []
    for record in due_cattle_records:
        days_overdue = (timezone.now().date() - record.next_vaccination_due).days
        due_cattle_list.append({
            "tagNo": record.tagno.tagno,
            "breed": record.breed,
            "age": f"{record.age_years} years, {record.age_months} months",
            "lastVaccination": record.last_vaccination_date.strftime('%Y-%m-%d') if record.last_vaccination_date else "N/A",
            "nextDueDate": record.next_vaccination_due.strftime('%Y-%m-%d') if record.next_vaccination_due else "N/A",
            "daysOverdue": days_overdue if days_overdue > 0 else 0,
            "vaccinationType": record.vaccination_type
        })
    
    # Get vaccinated cattle details
    vaccinated_cattle_records = queryset.filter(
        last_vaccination_date__isnull=False
    ).select_related('tagno').order_by('last_vaccination_date')
    
    vaccinated_cattle_list = []
    for record in vaccinated_cattle_records:
        vaccinated_cattle_list.append({
            "tagNo": record.tagno.tagno,
            "breed": record.breed,
            "age": f"{record.age_years} years, {record.age_months} months",
            "vaccinationType": record.vaccination_type,
            "lastVaccination": record.last_vaccination_date.strftime('%Y-%m-%d') if record.last_vaccination_date else "N/A",
            "nextDueDate": record.next_vaccination_due.strftime('%Y-%m-%d') if record.next_vaccination_due else "N/A",
            "color": record.color,
            "weight": record.weight
        })
    
    # Group by vaccine type
    vaccine_type_groups = {}
    for cattle in vaccinated_cattle_list:
        vac_type = cattle["vaccinationType"]
        if vac_type:  # Make sure we have a valid type
            if vac_type not in vaccine_type_groups:
                vaccine_type_groups[vac_type] = []
            vaccine_type_groups[vac_type].append(cattle)
    
    # Complete response data
    response_data = {
        "totalCattle": total_cattle,
        "vaccinated": vaccinated_cattle,
        "dueForVaccination": due_cattle,
        "vaccinationRate": vaccination_rate,
        "vaccineTypeDistribution": vaccine_data,
        "dueCattle": due_cattle_list,
        "vaccinatedCattle": vaccinated_cattle_list,
        "vaccineTypeGroups": vaccine_type_groups
    }
    
    return JsonResponse(response_data)