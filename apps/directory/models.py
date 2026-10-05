from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import TimeStampedModel

class State(TimeStampedModel):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True)
    abbreviation = models.CharField(max_length=2, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class City(TimeStampedModel):
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name="cities")
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=90)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "cities"
        constraints = [
            models.UniqueConstraint(fields=["state", "slug"], name="uniq_city_slug_per_state"),
        ]
    
    def __str__(self):
        return f"{self.name}, {self.state.abbreviation}"


class ClinicQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)
    
    def with_location(self):
        """One JOIN instead of two extra queries per clinic when rendering lists."""
        return self.select_related("city__state")

class Clinic(TimeStampedModel):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=170)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="clinics")

    address_line = models.CharField(max_length=200, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    description = models.TextField(blank=True)

    # Falls back to the city's coordinates when empty (used in Phase 6).
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    is_telehealth = models.BooleanField(default=False)
    # "Verified" is a strong public claim. Define your real criteria before
    # ever setting this to True on a live listing.
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=True)

    treatments = models.ManyToManyField("catalog.Treatment", related_name="clinics", blank=True)
    peptides = models.ManyToManyField(
        "catalog.Peptide", through="ClinicPeptide", related_name="clinics", blank=True
    )

    objects = ClinicQuerySet.as_manager()

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["city", "slug"], name="uniq_clinic_slug_per_city"),
        ]
        indexes = [
            models.Index(fields=["is_published", "city"], name="clinic_published_city_idx"),
        ]

    def __str__(self):
        return self.name

class ClinicPeptide(models.Model):
    """Association table with payload: which clinic offers which peptide, from what price."""

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="offerings")
    peptide = models.ForeignKey(
        "catalog.Peptide", on_delete=models.CASCADE, related_name="offerings"
    )
    price_from = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    price_note = models.CharField(max_length=120, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["clinic", "peptide"], name="uniq_clinic_peptide"),
        ]

    def __str__(self):
        return f"{self.clinic} - {self.peptide}"


class Review(TimeStampedModel):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="reviews")
    author_name = models.CharField(max_length=80)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=120, blank=True)
    body = models.TextField()
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.rating}/5 - {self.clinic}"
