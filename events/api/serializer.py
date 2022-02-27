from rest_framework import serializers
from .models import Events, EventsMeta, Auditorium, Ticket, Booking
from django.contrib.auth.models import User
import random
import string
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework import status
import pytz
from django.utils import timezone
from rest_framework.exceptions import APIException

utc = pytz.UTC
date_format = "%Y-%m-%dT%H:%M:%S.%f"


class CustomValidation(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'

    def __init__(self, detail, status_code):
        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = detail
        else:
            self.detail = self.default_detail


class AuditoriumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auditorium
        fields = ['auditorium_name', 'building_name']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["userid", "first_name", "username"]
        extra_kwargs = {
            "first_name": {"required": False},
            "userid": {"required": False},
            "username": {"required": False}
        }


class EventsMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventsMeta
        fields = '__all__'
        extra_kwargs = {
            'event_meta_id': {"required": False}
        }


class EventsSerializer(serializers.ModelSerializer):
    event_meta = EventsMetaSerializer(read_only=True)
    event_auditorium = AuditoriumSerializer(read_only=True)
    event_created_by = UserSerializer(read_only=True)

    class Meta:
        model = Events
        fields = "__all__"
        extra_kwargs = {
            'Event ID': {"required": False}
        }

    def validate_event_date(self, event_date_time):
        print("inside validate event date time")
        event_start_date_time = utc.localize(
            datetime.strptime(event_date_time, date_format))
        now = utc.localize(datetime.now())
        if now >= event_start_date_time:
            raise CustomValidation("event start date should be greater than current date",
                                   status.HTTP_400_BAD_REQUEST)

    def validate_booking_date(self, event_booking_start, event_booking_end, event_start_date_time):
        print("validate booking date")
        event_booking_start, event_booking_end = datetime.strptime(
            event_booking_start, date_format), datetime.strptime(event_booking_end, date_format)
        event_booking_start, event_booking_end = utc.localize(
            event_booking_start), utc.localize(event_booking_end)
        event_start_date_time = utc.localize(
            datetime.strptime(event_start_date_time, date_format))
        now = utc.localize(datetime.now())
        if not (event_booking_start > now and event_booking_end <= event_start_date_time and event_booking_end > event_booking_start):
            raise CustomValidation(
                "Invalid booking start date and end date, start date and end date should be in range of current and event date ", status_code=status.HTTP_400_BAD_REQUEST)

    def validate_auditorium(self, event_date_time, event_duration, auditorium):
        event_start_date_time = datetime.strptime(
            event_date_time, date_format)
        event_start_date_time = utc.localize(event_start_date_time)
        event_end_date_time = event_start_date_time + \
            timedelta(seconds=event_duration)
        bookings = Booking.objects.filter(
            event_auditorium=auditorium, event_start_date=event_start_date_time.date()).order_by("event_start_time")

        for booking in bookings:
            start, end = utc.localize(datetime.combine(booking.event_start_date, booking.event_start_time)), utc.localize(datetime.combine(
                booking.event_end_date, booking.event_end_time))
            if (event_start_date_time >= start and event_start_date_time < end) or (event_end_date_time > start and event_end_date_time <= end):
                raise CustomValidation(
                    "cannot book this auditorium in this slot", status_code=status.HTTP_400_BAD_REQUEST)

    def book_auditorium(self, event_date_time, event_duration, auditorium):
        print("inside book auditorium")
        event_end_date = utc.localize(datetime.strptime(
            event_date_time, date_format)) + timedelta(event_duration)
        auditorium.booked_till = event_date_time
        auditorium.is_booked = True
        return auditorium

    def validate_max_capacity(self, auditorium_capacity, max_capacity):
        print("inside validate max capacity")
        message = ""
        if max_capacity <= 0:
            message = "max capacity cannot be less than and equal to zero"
        elif max_capacity > auditorium_capacity:
            message = "max capacity cannot be greater than auditorium capacity"
        if len(message) > 0:
            raise CustomValidation(message, status.HTTP_400_BAD_REQUEST)

    def create(self, validated_data):
        meta = validated_data.pop("event_meta")
        auditorium = validated_data.pop("auditorium")
        user = validated_data.pop("user")
        aud = Auditorium.objects.filter(
            auditorium_name=auditorium['auditorium_name'], building_name=auditorium['building_name']).first()
        self.validate_event_date(validated_data["event_date_time"])
        if "event_booking_start" in meta and "event_booking_end" in meta:
            self.validate_booking_date(
                meta["event_booking_start"], meta["event_booking_end"], validated_data["event_date_time"])
        self.validate_auditorium(
            validated_data["event_date_time"], meta["event_duration"], aud)
        if "max_capacity" in meta:
            self.validate_max_capacity(
                aud.capacity, meta.get('max_capacity', 0))
        auditorium = self.book_auditorium(
            validated_data["event_date_time"], meta["event_duration"], aud)
        event_meta = EventsMetaSerializer.create(EventsMetaSerializer(), meta)

        if "max_capacity" not in meta:
            event_meta.curr_avail = aud.capacity
        else:
            event_meta.curr_avail = meta["max_capacity"]
        auditorium.save()
        event_meta.save()
        user = User.objects.filter(username=user['username']).first()
        event = Events.objects.create(
            event_meta=event_meta, **validated_data, event_auditorium=aud, event_created_by=user)
        start_date = datetime.strptime(event.event_date_time, date_format)
        end_date = start_date + \
            timedelta(seconds=event.event_meta.event_duration)
        booking = Booking.objects.create(event_auditorium=auditorium, event=event, event_start_date=start_date.date(
        ), event_end_date=end_date.date(), event_start_time=start_date.time(), event_end_time=end_date.time())
        booking.save()
        return event

    def update(self, instance, validated_data):
        auditorium_data = validated_data.get("auditorium", None)
        meta_data = validated_data.get("event_meta", None)

        # update of auditorium, expecting new building name and auditorium name when to change venue.
        newAuditorium = None
        if auditorium_data is not None:
            auditorium = instance.event_auditorium
            newAuditorium = Auditorium.objects.filter(
                auditorium_name=auditorium_data.get(
                    "auditorium_name", auditorium.auditorium_name),
                building_name=auditorium_data.get('building_name', auditorium.building_name)).first()
            if newAuditorium is not None:
                instance.event_auditorium = newAuditorium
            # free up exiting venue, if new has been selected
            if newAuditorium != auditorium:
                booking = Booking.objects.filter(
                    event_auditorium=auditorium, event=instance)
                booking.delete()

        # update event meta data if any
        if meta_data is not None:
            meta_instance = instance.event_meta
            meta_instance.event_duration = meta_data.get(
                'event_duration', meta_instance.event_duration)
            meta_instance.event_booking_start = meta_data.get(
                'event_booking_start', meta_instance.event_booking_start)
            meta_instance.event_booking_end = meta_data.get(
                'event_booking_end', meta_instance.event_booking_end)
            meta_instance.max_capacity = meta_data.get(
                'max_capacity', meta_instance.max_capacity)
            meta_instance.curr_avail = meta_data.get(
                'curr_avail', meta_instance.curr_avail)

        # update event instance
        instance.event_name = validated_data.get(
            'event_name', instance.event_name)
        instance.event_summary = validated_data.get(
            'event_summary', instance.event_summary)
        instance.event_date_time = validated_data.get(
            'event_date_time', instance.event_date_time)
        instance.event_price = validated_data.get(
            'event_price', instance.event_price)
        aud = instance.event_auditorium
        if newAuditorium is not None:
            aud = newAuditorium

        # validation based on updates
        self.validate_event_date(validated_data.get(
            "event_date_time", instance.event_date_time))

        # validate event bookin start and end
        if "event_booking_start" in meta_data or "event_booking_end" in meta_data:
            self.validate_booking_date(
                meta_data.get("event_booking_start", meta_instance.event_booking_start), meta_data.get("event_booking_end", meta_instance.event_booking_end), validated_data.get("event_date_time", instance.event_date_time))

        # validate if auditorium is available for new time
        self.validate_auditorium(validated_data.get(
            "event_date_time", instance.event_date_time), validated_data.get("event_duration", instance.event_meta.event_duration), aud)

        # set auditorium for booking
        auditorium = self.book_auditorium(validated_data.get(
            "event_date_time", instance.event_date_time),
            validated_data.get("event_duration", meta_instance.event_duration), aud)

        # check for capacity
        if "max_capacity" in meta_data:
            self.validate_max_capacity(
                aud.capacity, meta_data.get('max_capacity', 0))

        if "max_capacity" not in meta_data:
            meta_instance.curr_avail = aud.capacity
        else:
            meta_instance.curr_avail = meta_data["max_capacity"]

        # save up all instances
        auditorium.save()
        meta_instance.save()
        instance.event_meta = meta_instance
        instance.save()

        # create new booking
        start_date = datetime.strptime(instance.event_date_time, date_format)
        end_date = start_date + \
            timedelta(seconds=instance.event_meta.event_duration)
        booking = Booking.objects.create(
            event_auditorium=auditorium, event=instance, event_start_date=start_date.date(), event_end_date=end_date.date(), event_start_time=start_date.time(), event_end_time=end_date.time())
        booking.save()
        return instance


class TicketSerializer(serializers.Serializer):
    events = EventsSerializer(read_only=True)
    ticket_issue_to = UserSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ('payment_method', 'amount')

    def generateTicketNo(self):
        x = ''.join(random.choices(string.ascii_letters, k=4)) + "-" + \
            "".join(random.choices(string.digits, k=4))
        return x

    def validate_curr_availability(self, event):
        if event.event_meta.curr_avail <= 0:
            raise CustomValidation(
                "All tickets booked for this event", status_code=status.HTTP_200_OK)

    def create(self, validated_data, request_user):
        event_data = validated_data.pop("events")
        event = None
        if event_data is not None:
            event = Events.objects.filter(
                event_id=event_data['event_id']).first()
        if event:
            self.validate_curr_availability(event)
            tick_no = self.generateTicketNo()
            ticket = Ticket.objects.create(ticket_no=tick_no,
                                           ticket_issue_to=request_user, events=event, **validated_data)
            meta_instance = event.event_meta
            meta_instance.curr_avail = meta_instance.curr_avail - 1
            meta_instance.save()
            event.event_meta = meta_instance
            event.save()
            return ticket
        else:
            raise CustomValidation(
                "Event not found", status_code=status.HTTP_404_NOT_FOUND)
