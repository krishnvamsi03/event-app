from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Events, EventsMeta, Ticket, Auditorium, Booking, Place
import json
# Create your tests here.
createeventid = 1


class ListEventsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test", password="test@1233444", email="test@email.com")
        self.token = Token.objects.create(user=self.user)
        self.token.save()

    def test_listevents(self):
        response = self.client.get(
            '/api/list_event', HTTP_AUTHORIZATION='Token {}'.format(self.token.key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateEventTest(APITestCase):
    def setUp(self):
        self.adminUser = User.objects.create_user(
            username="admin", password="pass@1234", email="admin@email.com", is_staff=True)
        self.normalUser = User.objects.create_user(
            username="test", password="test@1234", email="test@test.com")
        self.adminToken = Token.objects.create(user=self.adminUser)
        self.userToken = Token.objects.create(user=self.normalUser)
        self.adminToken.save()
        self.userToken.save()
        self.place = Place.objects.create(
            street="testStreet", city="Mumbai", pincode=400104)
        self.audi1 = Auditorium.objects.create(
            place=self.place, auditorium_name="audi1", building_name="bldg1", capacity=100)
        self.audi2 = Auditorium.objects.create(
            place=self.place, auditorium_name="audi2", building_name="bldg1", capacity=200)
        self.audi2 = Auditorium.objects.create(
            place=self.place, auditorium_name="audi3", building_name="bldg1", capacity=300)

    def test_create_event_test(self):
        data = {
            "event_name": "Test event",
            "event_summary": "Test Summary",
            "event_date_time": "2022-03-04T23:32:00.000",
            "event_price": 230,
            "event_meta": {
                "event_duration": 3600,
                "curr_avail": 100,
                "event_booking_start": "2022-03-01T23:32:00.000",
                "event_booking_end": "2022-03-03T23:32:00.000"
            },
            "auditorium": {
                "auditorium_name": self.audi1.auditorium_name,
                "building_name": self.audi1.building_name
            },
            "user": {
                "username": self.adminUser.username
            }
        }
        response = self.client.post(
            "/api/create_event", content_type='application/json', data=json.dumps(data), HTTP_AUTHORIZATION='Token {}'.format(self.adminToken.key))
        print(response.data)
        eventid = response.data['eventid']
        createeventid = eventid

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(
            "/api/create_event", content_type='application/json', data=json.dumps(data), HTTP_AUTHORIZATION='Token {}'.format(self.userToken.key))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.post(
            "/api/create_event", content_type='application/json', data=json.dumps(data), HTTP_AUTHORIZATION='Token {}'.format(self.adminToken.key))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {
            "event_name": "Test event",
            "event_summary": "Test Summary",
            "event_date_time": "2022-03-04T23:32:00.000",
            "event_price": 230,
            "event_meta": {
                "event_duration": 3600,
                "curr_avail": 100,
                "event_booking_start": "2022-03-05T23:32:00.000",
                "event_booking_end": "2022-03-09T23:32:00.000"
            },
            "auditorium": {
                "auditorium_name": self.audi1.auditorium_name,
                "building_name": self.audi1.building_name
            },
            "user": {
                "username": self.adminUser.username
            }
        }
        response = self.client.post(
            "/api/create_event", content_type='application/json', data=json.dumps(data), HTTP_AUTHORIZATION='Token {}'.format(self.adminToken.key))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {
            "event_name": "Test event",
            "event_summary": "Test Summary",
            "event_date_time": "2022-03-04T23:32:00.000",
            "event_price": 230,
            "event_meta": {
                "event_duration": 3600,
                "curr_avail": 100,
                "event_booking_start": "2022-02-05T23:32:00.000",
                "event_booking_end": "2022-03-09T23:32:00.000"
            },
            "auditorium": {
                "auditorium_name": self.audi1.auditorium_name,
                "building_name": self.audi1.building_name
            },
            "user": {
                "username": self.adminUser.username
            }
        }
        response = self.client.post(
            "/api/create_event", content_type='application/json', data=json.dumps(data), HTTP_AUTHORIZATION='Token {}'.format(self.adminToken.key))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {
            "event_name": "Test event",
            "event_summary": "Test Summary",
            "event_date_time": "2022-02-04T23:32:00.000",
            "event_price": 230,
            "event_meta": {
                "event_duration": 3600,
                "curr_avail": 100,
                "event_booking_start": "2022-03-01T23:32:00.000",
                "event_booking_end": "2022-03-09T23:32:00.000"
            },
            "auditorium": {
                "auditorium_name": self.audi1.auditorium_name,
                "building_name": self.audi1.building_name
            },
            "user": {
                "username": self.adminUser.username
            }
        }
        response = self.client.post(
            "/api/create_event", content_type='application/json', data=json.dumps(data), HTTP_AUTHORIZATION='Token {}'.format(self.adminToken.key))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {
            "event_name": "Test event",
            "event_summary": "Test Summary",
            "event_date_time": "2022-03-04T23:32:00.000",
            "event_price": 230,
            "event_meta": {
                "event_duration": 3600,
                "event_booking_start": "2022-03-01T23:32:00.000",
                "event_booking_end": "2022-03-03T23:32:00.000",
                "max_capacity": -1
            },
            "auditorium": {
                "auditorium_name": self.audi2.auditorium_name,
                "building_name": self.audi1.building_name
            },
            "user": {
                "username": self.adminUser.username
            }
        }
        response = self.client.post(
            "/api/create_event", content_type='application/json', data=json.dumps(data), HTTP_AUTHORIZATION='Token {}'.format(self.adminToken.key))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "event_name": "Test event",
            "event_summary": "Test Summary",
            "event_date_time": "2022-03-04T23:32:00.000",
            "event_price": 230,
            "event_meta": {
                "event_duration": 3600,
                "event_booking_start": "2022-03-01T23:32:00.000",
                "event_booking_end": "2022-03-03T23:32:00.000",
                "max_capacity": 34
            },
            "auditorium": {
                "auditorium_name": self.audi2.auditorium_name,
                "building_name": self.audi1.building_name
            },
            "user": {
                "username": self.adminUser.username
            }
        }
        response = self.client.put(
            "/api/update_event/" + str(eventid), content_type='application/json', data=json.dumps(data), HTTP_AUTHORIZATION='Token {}'.format(self.adminToken.key))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {
            "event_name": "Test event",
            "event_summary": "Test Summary",
            "event_date_time": "2022-03-04T23:32:00.000",
            "event_price": 230,
            "event_meta": {
                "event_duration": 3600,
                "event_booking_start": "2022-03-01T23:32:00.000",
                "event_booking_end": "2022-03-03T23:32:00.000",
                "max_capacity": 50
            },
            "auditorium": {
                "auditorium_name": self.audi2.auditorium_name,
                "building_name": self.audi1.building_name
            },
            "user": {
                "username": self.adminUser.username
            }
        }
        response = self.client.put(
            "/api/update_event/" + str(eventid), content_type='application/json', data=json.dumps(data), HTTP_AUTHORIZATION='Token {}'.format(self.adminToken.key))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {
            "payment_method": "online",
            "amount": 133.3,
            "events": {
                "event_id": createeventid
            },
            "user": {
                "username": self.adminUser.username
            }
        }
        response = self.client.post("/api/book_ticket", content_type='application/json',
                                    data=json.dumps(data), HTTP_AUTHORIZATION='Token {}'.format(self.userToken.key))
        print(response.data)
        ticketid = response.data['ticketid']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get("/api/view_ticket/" + str(ticketid), content_type='application/json',
                                    HTTP_AUTHORIZATION='Token {}'.format(self.adminToken.key))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
