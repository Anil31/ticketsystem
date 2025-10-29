# tickets/models.py
from django.db import models
from django.core.validators import FileExtensionValidator, MinLengthValidator, validate_email
from django.utils import timezone

# --------- Hilfs-Validatoren ----------
MAX_UPLOAD_MB = 20
def validate_filesize(value):
    limit = MAX_UPLOAD_MB * 1024 * 1024  # 20 MB
    if value.size > limit:
        raise ValueError(f"Datei ist zu groß (>{MAX_UPLOAD_MB} MB).")

# --------- Stammdaten ----------
class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorien"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


# --------- Ticket ----------
class Ticket(models.Model):
    class Priority(models.TextChoices):
        LOW = "low", "Niedrig"
        MEDIUM = "medium", "Mittel"
        HIGH = "high", "Hoch"
        CRITICAL = "critical", "Kritisch"

    class Status(models.TextChoices):
        OPEN = "open", "Offen"
        IN_PROGRESS = "in_progress", "In Bearbeitung"
        RESOLVED = "resolved", "Gelöst"

    # Öffentliche Felder (kein Login -> Name & E-Mail Pflicht)
    name = models.CharField("Ihr Name", max_length=120, validators=[MinLengthValidator(2)])
    email = models.EmailField("Ihre E-Mail", validators=[validate_email])

    title = models.CharField("Titel", max_length=200)
    description = models.TextField("Beschreibung")

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Kategorie")
    priority = models.CharField("Priorität", max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField("Status", max_length=20, choices=Status.choices, default=Status.OPEN)

    created_at = models.DateTimeField("Erstellt am", default=timezone.now, editable=False)
    updated_at = models.DateTimeField("Aktualisiert am", auto_now=True)

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"#{self.pk} {self.title}"


# --------- Anhänge ----------
class Attachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="attachments", verbose_name="Ticket")

    # Typische Formate für Screenshots + PDF
    file = models.FileField(
        "Datei",
        upload_to="attachments/%Y/%m/%d",
        validators=[
            FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg", "gif", "pdf"]),
            validate_filesize,
        ],
    )
    original_name = models.CharField("Originaldateiname", max_length=255, blank=True)
    uploaded_by_name = models.CharField("Hochgeladen von (Name)", max_length=120, blank=True)
    uploaded_at = models.DateTimeField("Hochgeladen am", default=timezone.now, editable=False)

    class Meta:
        verbose_name = "Anhang"
        verbose_name_plural = "Anhänge"
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return self.original_name or (self.file.name.split("/")[-1] if self.file else "Anhang")

    def save(self, *args, **kwargs):
        # Fülle original_name automatisch, wenn leer
        if self.file and not self.original_name:
            self.original_name = self.file.name.split("/")[-1]
        super().save(*args, **kwargs)
