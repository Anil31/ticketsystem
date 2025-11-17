from django.urls import path
from .views import (
    ticket_create, ticket_thanks,
    internal_ticket_list, internal_ticket_detail, internal_dashboard,
    my_ticket_list, my_ticket_detail,
)

app_name = "tickets"

urlpatterns = [
    # Öffentlich / Mitarbeitende
    path("", ticket_create, name="ticket_create"),  
    path("tickets/new/", ticket_create, name="ticket_new"),
    path("tickets/me/",  my_ticket_list, name="my_tickets"),
    path("tickets/me/<int:pk>/", my_ticket_detail, name="my_ticket_detail"),
    path("thanks/", ticket_thanks, name="ticket_thanks"),

    # Intern (nur Staff)
    path("intern/", internal_dashboard, name="intern_dashboard"),            # /intern/
    path("intern/tickets/", internal_ticket_list, name="intern_ticket_list"),  # /intern/tickets/
    path("intern/tickets/<int:pk>/", internal_ticket_detail, name="intern_ticket_detail"),
]