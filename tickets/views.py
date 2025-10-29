# tickets/views.py
from django.shortcuts import render, redirect
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from .forms import TicketForm, AttachmentForm
from .models import Attachment

def _send_ticket_created_mail(ticket):
    subject = f"[Ticket #{ticket.id}] {ticket.title}"
    to = [ticket.email]
    txt = render_to_string("emails/ticket_created.txt", {"ticket": ticket})
    html = render_to_string("emails/ticket_created.html", {"ticket": ticket})

    msg = EmailMultiAlternatives(
        subject=subject,
        body=txt,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to,
        headers={"Reply-To": ticket.email},  # Antworten gehen an den User
    )
    msg.attach_alternative(html, "text/html")
    msg.send(fail_silently=False)

    # Optional: interne Kopie
    notify = getattr(settings, "SUPPORT_NOTIFY_EMAIL", None)
    if notify:
        copy = EmailMultiAlternatives(
            subject=f"[Kopie] {subject}",
            body=txt,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[notify],
        )
        copy.attach_alternative(html, "text/html")
        copy.send(fail_silently=True)

def ticket_create(request):
    if request.method == "POST":
        t_form = TicketForm(request.POST)
        a_form = AttachmentForm(request.POST, request.FILES)

        if t_form.is_valid() and a_form.is_valid():
            ticket = t_form.save()

            for f in a_form.cleaned_data.get("files", []):
                Attachment.objects.create(
                    ticket=ticket,
                    file=f,
                    uploaded_by_name=ticket.name,
                    original_name=f.name,
                )

            # >>> Mail versenden
            _send_ticket_created_mail(ticket)

            return redirect(reverse("ticket_thanks") + f"?id={ticket.pk}")
    else:
        t_form = TicketForm()
        a_form = AttachmentForm()

    return render(request, "tickets/create.html", {"t_form": t_form, "a_form": a_form})

def ticket_thanks(request):
    tid = request.GET.get("id")
    return render(request, "tickets/thanks.html", {"ticket_id": tid})
