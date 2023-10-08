import hmac
from hashlib import sha256
from urllib.parse import unquote
import json
import requests
from app import data
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from mysecrets import BOT_TOKEN, PROVIDER_TOKEN

# Create a secret key using HMAC for securing data
secret_key = hmac.new(b'WebAppData', bytes(BOT_TOKEN, encoding='utf-8'), sha256).digest()


# Define a view function to render the "make_order" page
def make_order(request):
    # Extract the 'init_message_id' from the request's GET parameters
    init_message_id = request.GET.get('init_message_id')

    if init_message_id is None:
        return HttpResponse("Bad Request", status=400)

    # Retrieve services and their JSON representation
    services, services_json = data.get_services_with_json()

    return render(
        request,
        'make_order.html',
        context={
            'init_message_id': int(init_message_id),
            'services': services, 'services_json': services_json
        }
    )


# Define a view function to get free appointment dates
def get_free_appointment_dates(request):
    # Retrieve free appointment dates from the data module
    free_dates = data.get_free_appointment_dates()

    return JsonResponse({
        'free_dates': free_dates
    })


# Define a view function to get active appointments for a user
def get_active_appointments(request):
    # Extract the 'bot_token' and 'user_id' from the request's GET parameters
    bot_token = request.GET.get('bot_token')

    if bot_token != BOT_TOKEN:
        return HttpResponse("Forbidden", status=403)

    user_id = request.GET.get('user_id')

    if user_id is None:
        return HttpResponse("Bad Request", status=400)

    # Retrieve active appointments for the specified user
    return JsonResponse({
        'active_appointments': data.get_active_appointments(int(user_id))
    })


# Define a view function to create an invoice link for payment
def create_invoice_link(request):
    # Extract data related to invoice creation from the request's GET parameters
    init_data_hash = request.GET.get('initDataHash')
    data_check_string = request.GET.get('dataCheckString')

    data_check_string_unquote = unquote(data_check_string.replace('&', '\n'))
    hash = hmac.new(secret_key, bytes(data_check_string_unquote, encoding='utf-8'), sha256).hexdigest()

    if hash != init_data_hash:
        return HttpResponse("Unauthorized", status=401)

    description = request.GET.get('description')
    payload = request.GET.get('payload')
    prices = request.GET.get('prices')

    if description is None or payload is None or prices is None:
        return HttpResponse("Bad Request", status=400)

    # Send a request to the Telegram Bot API to create an invoice link
    response = requests.get(
        f'https://api.telegram.org/bot{BOT_TOKEN}/createInvoiceLink',
        {
            'title': "Appointment",
            'description': description,
            'payload': payload,
            'provider_token': PROVIDER_TOKEN,
            'currency': 'USD',
            'prices': prices,
            'photo_url': 'https://images.pexels.com/photos/853427/pexels-photo-853427.jpeg?cs=srgb&dl=pexels-delbeautybox-853427.jpg&fm=jpg',
            'need_name': True,
            'need_phone_number': True
        }
    )

    return HttpResponse(response.text)


# Define a view function to make an appointment
def make_appointment(request):
    # Extract the 'bot_token', 'user_id', 'services_ids', 'date_iso', and 'time_iso'
    # from the request's GET parameters
    bot_token = request.GET.get('bot_token')

    if bot_token != BOT_TOKEN:
        return HttpResponse("Forbidden", status=403)

    user_id = int(request.GET.get('user_id'))
    services_ids = json.loads(request.GET.get('services_ids'))
    date_iso = request.GET.get('date_iso')
    time_iso = request.GET.get('time_iso')

    if user_id is None or services_ids is None or date_iso is None or time_iso is None:
        return HttpResponse("Bad Request", status=400)

    # Call a function to make an appointment using the extracted data
    data.make_appointment(user_id, services_ids, date_iso, time_iso)

    return HttpResponse("OK", status=200)
