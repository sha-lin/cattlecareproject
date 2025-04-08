from django.urls import path
from.import views
from .views import HomeTemplateView, AppointmentTemplateView, ManageAppointmentTemplateView

from django.urls import path
from .views import cattle_registration, download_cattle_excel, download_cattle_pdf

urlpatterns = [
    # path('vet/', cattle_registration, name='vet'),
    path('download-excel/', download_cattle_excel, name='download_cattle_excel'),
    path('download-pdf/', download_cattle_pdf, name='download_cattle_pdf'),
]
urlpatterns=[
    path('',views.index,name='index'),
    path('ab/',views.about),
    path('register/',views.reg,name='register'),
    path('login2/',views.sign, name='login2'),
    path('service/',views.service),
    path('farmer/', views.cattlereg, name='farmer'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('vet/', views.cattle_registration, name='cattle_registration'),
    path('download_report/<str:tagno>/', views.download_report, name='download_report'),

    
    path('catreg/',views.cattlereg),
    path('test/',views.test),
    path('profile/',views.profile),
    path('vaccinate/',views.vaccinate),
    path('logout/', views.logout_view, name='logout'),
    path('viewv/<int:id>/', views.view_vaccine, name='view_vaccine'),
    path('booking/<int:disease_id>/', views.booking, name='booking'),
    path('bookingii/<int:disease_id>/', views.booking2, name='bookingii'),
    path('vaccination-history/', views.vaccination_history, name='vaccination_history'),
    path('chpswd/',views.changepassword),
    path("make-an-appointment/", AppointmentTemplateView.as_view(), name="make-an-appointment"),
    path("manage-appointments/", ManageAppointmentTemplateView.as_view(), name="manage"),
    path("appointment/", HomeTemplateView.as_view(), name="home"),
    # path('health-records/cattles/<str:tagno>/', views.health_record_list, name='health_record_list'),
    # path('health-records/cattles/<str:tagno>/new/', views.health_record_create, name='health_record_create'),
    # path('health-records/<int:pk>/edit/', views.health_record_edit, name='health_record_edit'),
    # path('health-records/<int:pk>/delete/', views.health_record_delete, name='health_record_delete'),
    path('register-health-record/', views.cattlereg, name='cattlereg'),
    path('cattlereg/', views.cattlereg, name='cattlereg'),
    path('download-cattle-excel/', views.download_cattle_excel, name='download_cattle_excel'),
    path('download-cattle-pdf/', views.download_cattle_pdf, name='download_cattle_pdf'),
    path('cattle/<int:cattle_id>/nutrition/', views.cattle_nutrition, name='cattle_nutrition'),
    path('vaccination-dashboard/', views.vaccination_dashboard, name='vaccination_dashboard'),
    path('api/get_vaccination_data/', views.get_vaccination_data, name='get_vaccination_data'),
    # path('vet/dashboard/', views.vet_dashboard, name='vet_dashboard'),
    # path('vet/dashboard/respond_feedback/<int:feedback_id>/', views.respond_feedback, name='respond_feedback'),
    # path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),

    

    ]