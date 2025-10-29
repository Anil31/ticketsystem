# tickets/admin.py
from django.contrib import admin
from .models import Ticket, Category, Attachment

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    fields = ("file", "original_name", "uploaded_by_name", "uploaded_at")
    readonly_fields = ("uploaded_at",)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "priority", "category", "name", "email", "updated_at")
    list_filter = ("status", "priority", "category")
    search_fields = ("title", "description", "name", "email")
    readonly_fields = ("created_at", "updated_at")
    inlines = [AttachmentInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("ticket", "original_name", "uploaded_by_name", "uploaded_at")
    search_fields = ("original_name", "uploaded_by_name")
    list_filter = ("uploaded_at",)
    readonly_fields = ("uploaded_at",)
