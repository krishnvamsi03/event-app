from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Place(models.Model):
    place_id = models.AutoField(verbose_name="Place ID", primary_key=True,
                                unique=True, db_index=True, db_column="Place ID", auto_created=True)

    street = models.CharField(
        verbose_name="Building street", db_column="Street", max_length=100)
    city = models.CharField(verbose_name="Event city",
                            db_column="Event city", max_length=20)
    pincode = models.IntegerField(
        verbose_name="pincode", db_column="Pincode")

    def __str__(self):
        return str(self.street)


class Auditorium(models.Model):
    auditorium_id = models.AutoField(verbose_name="Auditorium ID", primary_key=True,
                                     unique=True, db_index=True, db_column="Auditorium ID", auto_created=True)
    auditorium_name = models.CharField(
        verbose_name="Auditorium name", db_column="Auditorium name", max_length=20, null=False, db_index=True)
    building_name = models.CharField(
        verbose_name="Event place", db_column="Event building", max_length=20)
    place = models.ForeignKey(
        to=Place, on_delete=models.CASCADE, db_column="Place", )
    capacity = models.IntegerField(
        verbose_name="Max capacity of auditorium", db_column="Capacity")
    booked_till = models.DateTimeField(
        db_column="Auditorium booked till", blank=True, null=True)
    is_booked = models.BooleanField(
        db_column="Auditorium already booked", blank=True, null=True)

    def __str__(self):
        return str(self.auditorium_name)


class EventsMeta(models.Model):
    event_meta_id = models.AutoField(
        primary_key=True, db_index=True, db_column="Event Meta ID")
    event_duration = models.IntegerField(
        verbose_name="Event duration (secs)", db_column="Event Duration")
    event_booking_start = models.DateTimeField(
        verbose_name="Event booking start Date and time", db_column="Booking start time", blank=True, null=True)
    event_booking_end = models.DateTimeField(
        verbose_name="Event booking end date", db_column="Booking end time", blank=True, null=True)
    max_capacity = models.IntegerField(
        verbose_name="Event max capacity", db_column="Event capacity", default=0)
    curr_avail = models.IntegerField(
        verbose_name="current availability", db_column="Event availability")

    def __str__(self):
        return str(self.curr_avail)


class Events(models.Model):
    event_id = models.AutoField(verbose_name="Event ID", primary_key=True,
                                unique=True, db_index=True, db_column="Event ID", auto_created=True)
    event_name = models.CharField(
        verbose_name="Event Name", max_length=20, db_column="Event Name", db_index=True)
    event_summary = models.CharField(
        verbose_name="Event Summary", max_length=255, db_column="Event Summary")
    event_date_time = models.DateTimeField(
        verbose_name="Event Date Time", db_column="Event Date Time")
    event_price = models.DecimalField(
        verbose_name="Event Price", db_column="Event Price", max_digits=7, decimal_places=2)
    event_meta = models.OneToOneField(to=EventsMeta, on_delete=models.CASCADE)
    event_auditorium = models.ForeignKey(
        to=Auditorium, on_delete=models.CASCADE)
    event_created_by = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return self.event_name


class Ticket(models.Model):
    ticket_id = models.AutoField(verbose_name="Ticket ID", primary_key=True,
                                 unique=True, db_index=True, db_column="Ticket ID", auto_created=True)
    ticket_no = models.CharField(
        db_column="Ticket no", unique=True, null=False, max_length=10)
    events = models.ForeignKey(to=Events, on_delete=models.CASCADE)
    payment_method = models.CharField(
        verbose_name="Mode of payment", db_column="Payment method", max_length=10)
    amount = models.DecimalField(
        verbose_name="Amount payable", db_column="Ticket price", max_digits=7, decimal_places=2)
    ticket_issue_to = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return self.ticket_no
