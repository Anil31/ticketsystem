from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from tickets import views as tviews

urlpatterns = [
    path("admin/", admin.site.urls),

    # Öffentlich
    path("", tviews.ticket_create, name="ticket_create"),
    path("danke/", tviews.ticket_thanks, name="ticket_thanks"),

    # Intern (Liste/Details/Statuswechsel)
    path("intern/tickets/", tviews.internal_ticket_list, name="intern_ticket_list"),
    path("intern/tickets/<int:pk>/", tviews.internal_ticket_detail, name="intern_ticket_detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
