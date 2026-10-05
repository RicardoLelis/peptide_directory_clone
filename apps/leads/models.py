from django.db import models

from apps.core.models import TimeStampedModel


class Inquiry(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        CLOSED = "closed", "Closed"

    clinic = models.ForeignKey(
        "directory.Clinic", on_delete=models.PROTECT, related_name="inquiries"
    )
    treatment = models.ForeignKey(
        "catalog.Treatment", on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    message = models.TextField(blank=True, help_text="Ask users not to include medical details.")
    consent = models.BooleanField(default=False)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.NEW)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "inquiries"

    def __str__(self):
        return f"{self.name} -> {self.clinic}"