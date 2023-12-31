from app.models import Service, Appointment
from django.core import serializers

import datetime

from django.db.models.query import QuerySet
from typing import Tuple, List, Dict


def get_services_with_json() -> Tuple[QuerySet, str]:

    services = Service.objects.all()
    services_json = serializers.serialize('json', services)

    return services, services_json
    

def get_free_appointment_dates() -> Dict[datetime.date.isoformat, List[datetime.time.isoformat]]:

    free_dates = dict()

    today = datetime.date.today()
    for i in range(7):
        date_iso = (today + datetime.timedelta(days=i)).isoformat()
        free_times = get_free_times(date_iso)
        if len(free_times) != 0:
            free_dates[date_iso] = free_times

    return free_dates


def get_free_times(date_iso: datetime.date.isoformat) -> List[datetime.time.isoformat]:

    free_times = list()

    hour_start = 11
    hour_end = 21
    if date_iso == datetime.date.today().isoformat():
        hour_now = datetime.datetime.now().hour
        if hour_start <= hour_now < hour_end - 1:
            hour_start = hour_now + 1
        elif hour_now > hour_end:
            hour_start = hour_end

    for h in range(hour_start, hour_end):
        time_iso = datetime.time(h).isoformat()
        if not Appointment.objects.filter(date=date_iso, time=time_iso).exists():
            free_times.append(time_iso)

    return free_times


def make_appointment(user_id: int,
    services_ids: List[int],
    date_iso: datetime.date.isoformat,
    time_iso: datetime.time.isoformat):

    appointment = Appointment.objects.create(user_id=user_id, services_ids=services_ids, date=date_iso, time=time_iso)
    appointment.save()


def get_active_appointments(user_id: int):

    active_appointments = Appointment.objects.filter(user_id=user_id, date__gte=datetime.date.today().isoformat()).order_by('date', 'time')
    active_appointments = [
        {
            'services_titles': [
                Service.objects.get(pk=service_id).title
                for service_id in active_appointment.services_ids
            ],
            'date': active_appointment.date,
            'time': active_appointment.time
        }
        for active_appointment in active_appointments
    ]

    return active_appointments
