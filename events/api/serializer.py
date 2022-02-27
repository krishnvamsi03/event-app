from rest_framework import serializers
from .models import Events, EventsMeta, Auditorium, Ticket
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

    def validate_auditorium(self, event_date_time, auditorium):
        event_date_time = datetime.strptime(
            event_date_time, date_format)
        event_date_time = utc.localize(event_date_time)
        if auditorium.booked_till >= event_date_time:
            raise CustomValidation("This auditorium is booked till " + str(
                auditorium.booked_till), status_code=status.HTTP_400_BAD_REQUEST)

    def book_auditorium(self, event_date_time, event_duration, auditorium):
        print("inside book auditorium")
        event_end_date = utc.localize(datetime.strptime(
            event_date_time, date_format)) + timedelta(event_duration)
        auditorium.booked_till = event_date_time
        auditorium.is_booked = True
        auditorium.save()
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
        self.validate_auditorium(validated_data["event_date_time"], aud)
        if "max_capacity" in meta:
            self.validate_max_capacity(
                aud.capacity, meta.get('max_capacity', 0))
        self.book_auditorium(
            validated_data["event_date_time"], meta["event_duration"], aud)
        event_meta = EventsMetaSerializer.create(EventsMetaSerializer(), meta)

        if "max_capacity" not in meta:
            event_meta.curr_avail = aud.capacity
        else:
            event_meta.curr_avail = meta["max_capacity"]
        event_meta.save()
        user = User.objects.filter(username=user['username']).first()
        event = Events.objects.create(
            event_meta=event_meta, **validated_data, event_auditorium=aud, event_created_by=user)
        return event

    def update(self, instance, validated_data):
        auditorium_data = validated_data.get("auditorium", None)
        meta_data = validated_data.get("event_meta", None)
        newAuditorium = None
        if auditorium_data is not None:
            auditorium = instance.event_auditorium
            newAuditorium = Auditorium.objects.filter(
                auditorium_name=auditorium_data.get(
                    "auditorium_name", auditorium.auditorium_name),
                building_name=auditorium_data.get('building_name', auditorium.building_name)).first()
            if newAuditorium is not None:
                instance.event_auditorium = newAuditorium
            if newAuditorium != auditorium:
                auditorium.is_booked = False
                auditorium.booked_till = datetime.now() - timedelta(60)
                auditorium.save()
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
        instance.event_name = validated_data.get(
            'event_name', instance.event_name)
        instance.event_summary = validated_data.get(
            'event_summary', instance.event_summary)
        instance.event_date_time = validated_data.get(
            'event_data_time', instance.event_date_time)
        instance.event_price = validated_data.get(
            'event_price', instance.event_price)
        aud = instance.event_auditorium
        if newAuditorium is not None:
            aud = newAuditorium
        self.validate_auditorium(aud)
        self.validate_event_date(validated_data.get(
            "event_date_time", instance.event_date_time))
        self.book_auditorium(
            self, validated_data.get(
                "event_date_time", instance.event_date_time),
            validated_data.get("event_duration", meta_instance.event_duration), aud)
        self.validate_max_capacity(
            aud.capacity, meta_data.get('max_capacity', 0))
        meta_instance.save()
        instance.event_meta = meta_instance
        instance.save()
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
        if event.curr_avail <= 0:
            return Response({"success": False, "message": "all tickets booked", "error": ""}, status=status.HTTP_200_OK)

    def create(self, validated_data):
        event_data = validated_data.pop("events")
        user_data = validated_data.pop("user")
        user, event = None, None
        if user_data is not None:
            user = User.objects.filter(username=user_data["username"]).first()
        if event_data is not None:
            event = Events.objects.filter(
                event_id=event_data['event_id']).first()
        if user and event:
            tick_no = self.generateTicketNo()
            self.validate_curr_availability(event)
            ticket = Ticket.objects.create(ticket_no=tick_no, events=event,
                                           ticket_issue_to=user, **validated_data)
            event.curr_avail = event.curr_avail - 1
            event.save()
            return ticket
