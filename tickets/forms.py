# tickets/forms.py
from django import forms
from django.core.validators import FileExtensionValidator
from .models import Ticket, MAX_UPLOAD_MB
import os

ALLOWED_EXTS = ["png", "jpg", "jpeg", "gif", "pdf"]

class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["name", "email", "title", "description", "category", "priority"]
        labels = {
            "name": "Ihr Name",
            "email": "Ihre E-Mail",
            "title": "Titel",
            "description": "Beschreibung",
            "category": "Kategorie",
            "priority": "Priorität",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }

class AttachmentForm(forms.Form):
    files = forms.FileField(
        label="Anhänge (optional)",
        required=False,
        widget=MultiFileInput(),
        help_text="Erlaubte Formate: PNG, JPG, PDF, GIF (max. ca. 20 MB pro Datei)",
    )

    def clean_files(self):
        return self.files.getlist("files")
        