# tickets/views.py
from django.shortcuts import render, redirect
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.shortcuts import get_object_or_404  
from django.core.paginator import Paginator      
from django.db.models import Q, Count                   
from django.contrib import messages              
from django.utils import timezone


from .forms import TicketForm
from .models import Attachment, Ticket

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

        if t_form.is_valid():
            ticket = t_form.save()

            # Dateien direkt aus request.FILES holen
            files = request.FILES.getlist("files")
            for f in files:
                Attachment.objects.create(
                    ticket=ticket,
                    file=f,
                    uploaded_by_name=ticket.name,
                    original_name=f.name,
                )

            _send_ticket_created_mail(ticket)
            return redirect(reverse("ticket_thanks") + f"?id={ticket.pk}")
    else:
        t_form = TicketForm()

    return render(request, "tickets/create.html", {"t_form": t_form})

def ticket_thanks(request):
    tid = request.GET.get("id")
    return render(request, "tickets/thanks.html", {"ticket_id": tid})

# --- Interne Liste ---
def internal_ticket_list(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    qs = Ticket.objects.all().order_by("-updated_at")
    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(name__icontains=q) |
            Q(email__icontains=q)
        )

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "tickets/intern_list.html",
        {
            "page_obj": page_obj,
            "q": q,
            "status": status,
            "statuses": Ticket.Status.choices,
        },
    )

# --- Interne Detailseite + Status ändern ---
def internal_ticket_detail(request, pk):
    t = get_object_or_404(Ticket, pk=pk)

    if request.method == "POST":
        new_status = request.POST.get("status")
        allowed = dict(Ticket.Status.choices).keys()
        if new_status in allowed:
            t.status = new_status
            t.save()
            messages.success(request, "Status aktualisiert.")
            return redirect("intern_ticket_detail", pk=t.pk)
        else:
            messages.error(request, "Ungültiger Status.")
            return redirect("intern_ticket_detail", pk=t.pk)

    return render(request, "tickets/intern_detail.html", {"ticket": t})


def internal_dashboard(request):

    # Status-KPIs
    total = Ticket.objects.count()
    count_open = Ticket.objects.filter(status=Ticket.Status.OPEN).count()
    count_progress = Ticket.objects.filter(status=Ticket.Status.IN_PROGRESS).count()
    count_resolved = Ticket.objects.filter(status=Ticket.Status.RESOLVED).count()

    # Verteilung nach Priorität (nur offene Tickets – aussagekräftiger)
    open_by_prio = (
        Ticket.objects.filter(status=Ticket.Status.OPEN)
        .values("priority")
        .annotate(c=Count("id"))
    )
    prio_map = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for row in open_by_prio:
        prio_map[row["priority"]] = row["c"]

    # Letzte Tickets (zuletzt aktualisiert)
    recent = Ticket.objects.all().order_by("-updated_at")[:8]

    # Tickets in den letzten 7 Tagen (erstellt)
    today = timezone.localdate()
    last7 = []
    for i in range(6, -1, -1):
        day = today - timezone.timedelta(days=i)
        n = Ticket.objects.filter(created_at__date=day).count()
        last7.append({"date": day, "count": n})

    ctx = {
        "total": total,
        "count_open": count_open,
        "count_progress": count_progress,
        "count_resolved": count_resolved,
        "prio_open_low": prio_map["low"],
        "prio_open_medium": prio_map["medium"],
        "prio_open_high": prio_map["high"],
        "prio_open_critical": prio_map["critical"],
        "recent": recent,
        "last7": last7,
    }
    return render(request, "tickets/intern_dashboard.html", ctx)