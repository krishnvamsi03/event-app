from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status, request
from .constants import HTTPMethods
from .models import Events, EventsMeta, Ticket
from datetime import datetime
from .serializer import EventsMetaSerializer, EventsSerializer, TicketSerializer, CustomValidation
import json
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import authentication_classes, permission_classes
# Create your views here.


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def list_events(request: request):
    if request.method == "GET":
        responseData = {"content": [], "no_of_events": 0}
        events = Events.objects.all()
        for event in events:
            sub = {
                "event_name": event.event_name,
                "event_summary": event.event_summary,
                "event_date": event.event_date_time,
                "event_price": event.event_price
            }
            responseData["content"].append(sub)
            responseData["no_of_events"] += 1
        return Response(responseData, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_event(request):
    if request.method == "POST":
        serializeObj = EventsSerializer(data=request.data)
        response = {"success": True, "errors": "", "message": ""}
        if serializeObj.is_valid(raise_exception=True):
            try:
                serializeObj.create(request.data)
                response["message"] = "Event created successfully"
                return Response(response, status=status.HTTP_201_CREATED)
            except Exception as e:
                response["success"] = False
                response["errors"] = str(e)
                response["message"] = "failed to create event"
                return Response(response, status=e.status_code)
        else:
            response["success"] = False
            response["errors"] = json.dumps(serializeObj.errors)
            response["message"] = "some data is missing, invalid json object"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PUT"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_event(request, id):
    if request.method == "PUT":
        event = Events.objects.filter(event_id=id).first()
        responseData = {"success": True, "message": "", "error": ""}
        if event is not None:
            serializeObj = EventsSerializer(
                instance=event, data=request.data, partial=True)
            if serializeObj.is_valid():
                serializeObj.update(event, request.data)
                responseData['message'] = "updated successfully"
                return Response(responseData, status=status.HTTP_200_OK)
            else:
                responseData['success'] = False
                responseData['message'] = "failed to update resource due to invalid json"
                responseData['error'] = json.dumps(serializeObj.errors)
                return Response(responseData, status=status.HTTP_400_BAD_REQUEST)
        else:
            responseData["success"] = False
            responseData["message"] = "resource not found"
            return Response(responseData, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def book_ticket(request):
    if request.method == "POST":
        serializeObj = TicketSerializer(data=request.data)
        responseData = {"success": False, "message": "", "errors": ""}
        if serializeObj.is_valid():
            try:
                serializeObj.create(request.data)
                responseData["success"] = True
                responseData["message"] = "Ticket booked successfully"
                return Response(responseData, status=status.HTTP_201_CREATED)
            except Exception as e:
                responseData["message"] = "failed to book ticket"
                responseData["errors"] = str(e)
                return Response(responseData, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            responseData["message"] = "invalid json object"
            responseData["errors"] = json.dumps(serializeObj.errors)
            return Response(responseData, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def view_ticket(request, id):
    if request.method == "GET":
        ticket = Ticket.objects.filter(ticket_id=id).first()
        responseData = {"success": False,
                        "message": "", "error": "", "content": {}}
        if ticket is not None:
            responseData["content"] = {
                "ticket_no": ticket.ticket_no,
                "ticket_price": ticket.amount,
                "event": ticket.events.event_name,
                "issued_to": ticket.ticket_issue_to.username
            }
            responseData["success"] = True
            responseData["message"] = "resource found"
            return Response(responseData, status=status.HTTP_200_OK)
        else:
            responseData["message"] = "Resource not found"
            return Response(responseData, status=status.HTTP_404_NOT_FOUND)
