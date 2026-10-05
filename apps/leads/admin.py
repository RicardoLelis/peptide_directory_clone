from django.contrib import admin

from .models import Inquiry


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "clinic", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "email")
    list_select_related = ("clinic",)
    readonly_fields = ("created_at", "updated_at")