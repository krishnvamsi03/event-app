from django.db import models

# Create your models here.


class Events(models.Model):
    event_id = models.IntegerField(verbose_name="Event ID", primary_key=True,
                                   unique=True, db_index=True, name="Event ID", auto_created=True)
    event_name = models.CharField(
        verbose_name="Event Name", max_length=20, name="Event Name", db_index=True)
    event_summary = models.CharField(
        verbose_name="Event Summary", max_length=255, name="Event Summary")
    event_date_time = models.DateTimeField(
        verbose_name="Event Date Time", name="Event Date Time")
    event_price = models.DecimalField(
        verbose_name="Event Price", name="Event Price", max_digits=7, decimal_places=2)
    # auditorium and created by is pending


class EventsMeta(models.Model):
    event = models.OneToOneField(
        to=Events, on_delete=models.CASCADE, primary_key=True)
    event_duration = models.IntegerField(
        verbose_name="Event duration (secs)", name="Event Duration")
    event_booking_start = models.DateTimeField(
        verbose_name="Event booking start Date and time", name="Booking start time", null=True)
    event_booking_end = models.DateTimeField(
        verbose_name="Event booking end date", name="Booking end time", null=True)
    max_capacity = models.IntegerField(
        verbose_name="Event max capacity", name="Event capacity", default=0)
    curr_avail = models.IntegerField(
        verbose_name="current availability", name="Event availability")


class Place(models.Model):
    place_id = models.IntegerField(verbose_name="Place ID", primary_key=True,
                                   unique=True, db_index=True, name="Place ID", auto_created=True)
    building = models.CharField(
        verbose_name="Event place", name="Event building", max_length=20)
    street = models.CharField(
        verbose_name="Building street", name="Street", max_length=100)
    city = models.CharField(verbose_name="Event city",
                            name="Event city", max_length=20)
    pincode = models.IntegerField(
        verbose_name="pincode", name="Pincode")


class Auditorium(models.Model):
    auditorium_id = models.IntegerField(verbose_name="Auditorium ID", primary_key=True,
                                        unique=True, db_index=True, name="Auditorium ID", auto_created=True)
    auditorium_name = models.CharField(
        verbose_name="Auditorium name", name="Auditorium name", max_length=20, null=False, db_index=True)
    place = models.OneToOneField(
        verbose_name="lookup to Auditorium", name="Place", to=Place, on_delete=models.CASCADE)
    capacity = models.IntegerField(
        verbose_name="Max capacity of auditorium", name="Capacity")


class Ticket(models.Model):
    ticket_id = models.IntegerField(verbose_name="Auditorium ID", primary_key=True,
                                    unique=True, db_index=True, name="Auditorium ID", auto_created=True)
    ticket_no = models.CharField(
        name="Ticket no", unique=True, null=False, max_length=10)
    events = models.OneToOneField(to=Events, on_delete=models.CASCADE)
    payment_method = models.CharField(
        verbose_name="Mode of payment", name="Payment method", max_length=10)
    amount = models.DecimalField(
        verbose_name="Amount payable", name="Ticket price", max_digits=7, decimal_places=2)
