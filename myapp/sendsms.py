import requests

url = "https://api.sandbox.africastalking.com/version1/messaging"

headers = {'ApiKey': 'atsk_4f66efb1a8ff2875402127193b31351e85d6059b46b9093890c15ed7fe8cd72a6f526514', 
           'Content-Type': 'application/x-www-form-urlencoded',
           'Accept': 'application/json'}

data = {'username': 'sandbox',
        'from': '16536',
        'message': "Hello world !",
        'to': '+254701338496'}


def make_post_request():  
    response = requests.post( url = url, headers = headers, data = data )
    return response


print( make_post_request().json() )
