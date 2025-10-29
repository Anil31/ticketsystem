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
        widget=MultiFileInput(),   # <- statt ClearableFileInput(attrs={"multiple": True})
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTS)],
        help_text=f"Erlaubt: {', '.join(ALLOWED_EXTS)} • Max {MAX_UPLOAD_MB} MB pro Datei",
    )

    def clean_files(self):
        data = self.files.getlist("files")
        for f in data:
            ext = os.path.splitext(f.name)[1].lstrip(".").lower()
            if ext not in ALLOWED_EXTS:
                raise forms.ValidationError(f"Dateityp '{ext}' ist nicht erlaubt.")
            if f.size > MAX_UPLOAD_MB * 1024 * 1024:
                raise forms.ValidationError(f"Datei '{f.name}' ist größer als {MAX_UPLOAD_MB} MB.")
        return data
