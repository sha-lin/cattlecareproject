# In your cattle app (e.g., cattle/signals.py)

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CattleRecord
from smsapp.utils import send_sms  # Import your SMS sending function

@receiver(post_save, sender=CattleRecord)
def notify_farmer_about_vaccination(sender, instance, created, **kwargs):
    # Check if this record includes vaccination information
    if instance.next_vaccination_due and instance.vaccination_type:
        # Get the cattle object
        cattle = instance.tagno  # This is the ForeignKey to Cattle model
        
        # Get the farmer's phone number
        farmer_phone = cattle.owner.phone  # Using the correct phone field from your Farmer model
        
        # Format the date for readability
        formatted_date = instance.next_vaccination_due.strftime('%d %b, %Y')  # e.g., "25 Apr, 2025"
        
        # Compose the message
        message = (f"Dear {cattle.owner.name}, your cattle with tag {cattle.tagno} is due for "
                   f"{instance.vaccination_type} vaccination on {formatted_date}. "
                   f"Please prepare accordingly.")
        
        # Send the SMS
        send_sms(farmer_phone, message)