from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status, request
from .constants import HTTPMethods
from .models import Events, EventsMeta
from datetime import datetime
from .serializer import EventsMetaSerializer, EventsSerializer
import json
# Create your views here.


@api_view(["GET"])
def list_events(request: request):
    if request == HTTPMethods.GET:
        response = {"events": [], "no_of_events": 0,
                    "success": True, "error": ""}
        events = Events.objects.all().filter(event_date_time >= datetime.now())
        for event in events:
            currRes = {
                "event_name": event.event_name,
                "event_summary": event.event_summary,
                "event_price": event.event_price,
                "event_date": event.event_date_time.strftime("%d-%m-%Y %H:%M:%S"),
                "event_duration": "",
                "booking_start": "",
                "booking_end": "",
                "max_capacity": "",
                "curr_availability": -1
            }
            eventMeta = EventsMeta.objects.all().filter(event=event)
            if eventMeta is not None:
                currRes["event_duration"] = eventMeta.event_duration
                currRes["booking_start"] = eventMeta.event_booking_start
                currRes["booking_end"] = eventMeta.event_booking_end
                currRes["max_capacity"] = eventMeta.max_capacity
                currRes["curr_availability"] = eventMeta.curr_avail
            response.events.append(currRes)
        response["no_of_events"] = len(response['events'])
        return Response(response, status=status.HTTP_200_OK)


@api_view(["POST"])
def create_event(request):
    if request.method == "POST":
        serializeObj = EventsSerializer(data=request.data)
        response = {"success": True, "errors": "", "message": ""}
        if serializeObj.is_valid():
            try:
                serializeObj.save()
                response["message"] = "Event created successfully"
                return Response(response, status=status.HTTP_201_CREATED)
            except Exception as e:
                response["success"] = False
                response["errors"] = str(e)
                response["message"] = "failed to create event"
                return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            print("inside in valid data")
            response["success"] = False
            response["errors"] = json.dumps(serializeObj.errors)
            response["message"] = "some data is missing, invalid json object"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PUT"])
def update_event(request):
    if request == HTTPMethods.PUT:
        event = Events.objects.all().filter(event_id=request.data.get("Event id", 0))
        response = {"success": True, "errors": "", "message": ""}
        if event is not None:
            serializeObj = EventsSerializer(event, data=request.data)
            if serializeObj.is_valid():
                try:
                    serializeObj.save()
                except Exception as e:
                    response["success"] = False
                    response["errors"] = str(e)
                    response["message"] = "failed to update record"
                    return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                response["message"] = "some data is missing, invalid json object"
        response["success"] = False
        response["errors"] = str(serializeObj.errors)
        response["message"] = "event not found"
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
