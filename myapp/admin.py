from django.contrib import admin
from .models import User, Farmer, Vet, Cattle, CattleRecord, Vaccination, Appointment
from smsapp.utils import send_sms

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_admin', 'is_farmer', 'is_vet')

@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')

@admin.register(Vet)
class VetAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')

@admin.register(Cattle)
class CattleAdmin(admin.ModelAdmin):
    list_display = ('tagno', 'breed', 'gender', 'dob', 'age_months', 'age_years', 'weight', 'color', 'owner')

@admin.register(CattleRecord)
class CattleRecordAdmin(admin.ModelAdmin):
    list_display = ('tagno','breed', 'gender', 'dob', 'vaccination_type', 'last_vaccination_date','next_vaccination_due', 'age_months', 'age_years', 'observation', 'disease_diagnosis', 'weight', 'color')
    actions = ['send_vaccination_reminder']
    
    def send_vaccination_reminder(self, request, queryset):
        success_count = 0
        error_count = 0
        
        for record in queryset:
            if record.next_vaccination_due and record.vaccination_type:
                cattle = record.tagno
                farmer_phone = cattle.owner.phone
                
                formatted_date = record.next_vaccination_due.strftime('%d %b, %Y')
                
                message = (f"Dear {cattle.owner.name}, your cattle with tag {cattle.tagno} is due for "
                          f"{record.vaccination_type} vaccination on {formatted_date}. "
                          f"Please prepare accordingly.")
                
                success, response = send_sms(farmer_phone, message)
                if success:
                    success_count += 1
                else:
                    error_count += 1
        
        if error_count:
            self.message_user(
                request, 
                f"Successfully sent {success_count} vaccination reminders. Failed to send {error_count} reminders.",
                level='WARNING' if error_count > 0 else 'SUCCESS'
            )
        else:
            self.message_user(request, f"Successfully sent {success_count} vaccination reminders.")
    
    send_vaccination_reminder.short_description = "Send vaccination reminders to farmers"
@admin.register(Vaccination)
class VaccinationAdmin(admin.ModelAdmin):
    list_display = ('cattle', 'vaccine', 'date', 'status')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('vet', 'fname', 'lname', 'email', 'mobile','request_details',  'status', 'appointment_date','accepted', 'accepted_date' )
   




