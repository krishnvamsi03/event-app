from django.urls import path
from . import views

urlpatterns = [
    path('create_event', views.create_event, name="create"),
    path('update_event/<int:id>', views.update_event, name="update"),
    path('list_event', views.list_events, name="list"),
    path('book_ticket', views.book_ticket, name="book"),
    path('view_events', views.list_events, name="view"),
    path('view_ticket/<int:id>', views.view_ticket, name="view_ticket")
]
