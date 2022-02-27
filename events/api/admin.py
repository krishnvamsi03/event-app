from django.contrib import admin
from .models import Events, EventsMeta, Place, Ticket, Auditorium, Booking
# Register your models here.


@admin.register(Events)
class EventAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Events._meta.fields]


@admin.register(EventsMeta)
class EventMetaAdmin(admin.ModelAdmin):
    list_display = [f.name for f in EventsMeta._meta.fields]


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Place._meta.fields]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Ticket._meta.fields]


@admin.register(Auditorium)
class AuditoriumAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Auditorium._meta.fields]

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Booking._meta.fields]
