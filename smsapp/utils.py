# smsapp/utils.py

import africastalking
from django.conf import settings

def send_sms(phone_number, message):
    # Initialize Africa's Talking
    username = settings.AT_USER_NAME
    api_key = settings.AT_API_KEY
    
    africastalking.initialize(username, api_key)
    sms = africastalking.SMS
    
    # Remove any spaces in the phone number and ensure it has country code
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number
    
    # Send the message
    try:
        response = sms.send(message, [phone_number])
        return True, response
    except Exception as e:
        # Log the error
        print(f"Error sending SMS: {e}")
        return False, str(e)