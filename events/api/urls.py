from django.urls import path
from . import views

urlpatterns = [
    path('create_event', views.create_event, name="create"),
    path('update_event', views.update_event, name="update"),
    path('list_event', views.list_events, name="list"),
]
