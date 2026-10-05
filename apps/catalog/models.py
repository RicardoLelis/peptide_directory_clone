from django.db import models

from apps.core.models import TimeStampedModel

# Full class names must appear literally so tailwind's scanner can  see them
TINT_CLASSES = {
    "mint": "bg-tint-mint",
    "peach": "bg-tint-peach",
    "rose": "bg-tint-rose",
    "lavender": "bg-tint-lavender",
    "sky": "bg-tint-sky",
}

# These live in styles.css, so the status enum maps straight onto them.
BADGE_CLASSES = {
    "fda_approved": "badge-fda",
    "compoundable": "badge-compound",
    "research_use": "badge-research",
}

class Treatment(TimeStampedModel):
    class Tint(models.TextChoices):
        MINT = "mint", "Mint"
        PEACH = "peach", "Peach"
        ROSE = "rose", "Rose"
        LAVENDER = "lavender", "Lavender"
        SKY = "sky", "Sky"
    
    name = models.CharField(max_length=80, unique=True)
    slug = models.CharField(max_length=90, unique=True)
    tagline = models.CharField(max_length=160, help_text="One-liner on the category card.")
    tint = models.CharField(max_length=10, choices=Tint.choices, default=Tint.MINT)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name
    
    @property
    def tint_class(self):
        return TINT_CLASSES[self.tint]

class PeptideQuerySet(models.QuerySet):
    def popular(self):
        return self.filter(is_popular=True)


class Peptide(TimeStampedModel):
    class RegulatoryStatus(models.TextChoices):
        FDA_APPROVED = "fda_approved", "FDA Approved"
        COMPOUNDABLE = "compoundable", "Compoundable"
        RESEARCH_USE = "research_use", "Research Use"
    
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=130, unique=True)
    regulatory_status = models.CharField(
        max_length=20, choices=RegulatoryStatus.choices, db_index=True
    )
    drug_class = models.CharField(max_length=120)
    summary = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    is_popular = models.BooleanField(default=False)
    treatments = models.ManyToManyField(Treatment, related_name="peptides", blank=True)

    objects = PeptideQuerySet.as_manager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
    
    @property
    def badge_class(self):
        return BADGE_CLASSES[self.regulatory_status]

class Protocol(TimeStampedModel):
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=170, unique=True)
    treatment = models.ForeignKey(Treatment, on_delete=models.PROTECT, related_name="protocols")
    peptides = models.ManyToManyField(Peptide, related_name="protocols", blank=True)
    summary = models.CharField(max_length=255)
    body = models.TextField(blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title




