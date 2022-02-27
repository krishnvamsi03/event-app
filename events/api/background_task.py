from .models import Auditorium
from datetime import datetime, timedelta
from django.utils import timezone
from threading import Thread
import time
import pytz


def check_auditorium():
    auditoriums = Auditorium.objects.filter(booked_till__lt=datetime.now(tz=timezone.utc))
    for aud in auditoriums:
        aud.booked_till = datetime.now(tz=timezone.utc)
        aud.is_booked = False
        aud.save()
    time.sleep(60)


def main():
    t1 = Thread(target=check_auditorium)
    t1.start()
