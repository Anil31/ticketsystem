# helpdesk/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from tickets import views as tviews

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", tviews.ticket_create, name="ticket_create"),      # Startseite = Formular
    path("danke/", tviews.ticket_thanks, name="ticket_thanks"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
