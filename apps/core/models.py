from django.db import models

class TimeStampedModel(models.Model):
    """Adds created/updated audit columns. Abbstract: created no table itself."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True