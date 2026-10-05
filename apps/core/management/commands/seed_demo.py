from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from apps.catalog.models import Peptide, Protocol, Treatment
from apps.content.models import Post, PostCategory
from apps.directory.models import City, Clinic, ClinicPeptide, Review, State

Tint = Treatment.Tint
Status = Peptide.RegulatoryStatus

# Every row is keyed by MODEL FIELD NAME, so values can't land in the wrong column.
# Enum members (Tint.MINT, Status.FDA_APPROVED) mean a typo raises AttributeError
# instead of silently saving a bad string.

TREATMENTS = [
    {"name": "Weight Loss", "tagline": "Clinics offering supervised weight programs.", "tint": Tint.MINT},
    {"name": "Anti-Aging & Longevity", "tagline": "Providers focused on healthy aging.", "tint": Tint.PEACH},
    {"name": "Tissue Repair & Recovery", "tagline": "Options aimed at injury recovery.", "tint": Tint.ROSE},
    {"name": "Hormone Optimization", "tagline": "Hormone-related protocols and providers.", "tint": Tint.SKY},
    {"name": "Cognitive Enhancement", "tagline": "Focus and memory support options.", "tint": Tint.LAVENDER},
    {"name": "Sexual Wellness", "tagline": "Clinically guided wellness options.", "tint": Tint.PEACH},
    {"name": "Athletic Performance", "tagline": "Strength, endurance and recovery.", "tint": Tint.MINT},
    {"name": "Immune Support", "tagline": "Immune-related protocols.", "tint": Tint.SKY},
]

PEPTIDES = [
    {
        "name": "Semaglutide",
        "regulatory_status": Status.FDA_APPROVED,
        "drug_class": "GLP-1 Receptor Agonist",
        "summary": "Demo summary: GLP-1 medication profile.",
        "is_popular": True,
        "treatments": ["weight-loss"],  # popped before saving; used for the M2M below
    },
    {
        "name": "Tirzepatide",
        "regulatory_status": Status.FDA_APPROVED,
        "drug_class": "GIP/GLP-1 Receptor Agonist",
        "summary": "Demo summary: dual-agonist medication profile.",
        "is_popular": True,
        "treatments": ["weight-loss"],
    },
    {
        "name": "BPC-157",
        "regulatory_status": Status.RESEARCH_USE,
        "drug_class": "Synthetic Fragment",
        "summary": "Demo summary: research-use compound profile.",
        "is_popular": True,
        "treatments": ["tissue-repair-recovery", "athletic-performance"],
    },
    {
        "name": "Retatrutide",
        "regulatory_status": Status.RESEARCH_USE,
        "drug_class": "Triple Incretin Agonist",
        "summary": "Demo summary: investigational compound profile.",
        "is_popular": True,
        "treatments": ["weight-loss"],
    },
    {
        "name": "Sermorelin",
        "regulatory_status": Status.COMPOUNDABLE,
        "drug_class": "Growth Hormone Releasing Hormone",
        "summary": "Demo summary: compounded peptide profile.",
        "is_popular": True,
        "treatments": ["anti-aging-longevity", "hormone-optimization"],
    },
    {
        "name": "CJC-1295 / Ipamorelin",
        "regulatory_status": Status.COMPOUNDABLE,
        "drug_class": "Growth Hormone Secretagogue",
        "summary": "Demo summary: secretagogue stack profile.",
        "is_popular": True,
        "treatments": ["anti-aging-longevity", "athletic-performance"],
    },
]

PROTOCOLS = [
    {
        "title": "Weight Loss & GLP-1 Overview",
        "treatment": "weight-loss",
        "peptides": ["semaglutide", "tirzepatide"],
        "summary": "Demo protocol overview.",
    },
    {
        "title": "Tissue Repair Overview",
        "treatment": "tissue-repair-recovery",
        "peptides": ["bpc-157"],
        "summary": "Demo protocol overview.",
    },
]

GEO = [
    {
        "name": "Tennessee",
        "abbreviation": "TN",
        "cities": [
            {"name": "Nashville", "latitude": 36.1627, "longitude": -86.7816},
            {"name": "Memphis", "latitude": 35.1495, "longitude": -90.0490},
        ],
    },
    {
        "name": "Texas",
        "abbreviation": "TX",
        "cities": [
            {"name": "Austin", "latitude": 30.2672, "longitude": -97.7431},
            {"name": "Houston", "latitude": 29.7604, "longitude": -95.3698},
        ],
    },
    {
        "name": "Florida",
        "abbreviation": "FL",
        "cities": [{"name": "Miami", "latitude": 25.7617, "longitude": -80.1918}],
    },
    {
        "name": "California",
        "abbreviation": "CA",
        "cities": [{"name": "Los Angeles", "latitude": 34.0522, "longitude": -118.2437}],
    },
    {
        "name": "New York",
        "abbreviation": "NY",
        "cities": [{"name": "New York", "latitude": 40.7128, "longitude": -74.0060}],
    },
]

CLINIC_SUFFIXES = ["Wellness Clinic", "Peptide Medical Group"]

REVIEWS = [
    {"author_name": "Demo Patient A", "rating": 5, "title": "Clear and helpful"},
    {"author_name": "Demo Patient B", "rating": 4, "title": "Good experience"},
]

CATEGORIES = ["News", "How-To Guides", "Weight Loss Meds"]

POSTS = [
    {"title": "Demo news post", "category": "News"},
    {"title": "Demo how-to: reading a peptide profile", "category": "How-To Guides"},
    {"title": "Demo guide: questions to ask a clinic", "category": "Weight Loss Meds"},
]


class Command(BaseCommand):
    help = "Load idempotent demo data (fictional clinics and posts) for development."

    @transaction.atomic
    def handle(self, *args, **options):
        treatments = self._treatments()
        peptides = self._peptides(treatments)
        self._protocols(treatments, peptides)
        self._clinics(treatments, peptides)
        self._posts(peptides)
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded: {Treatment.objects.count()} treatments, "
                f"{Peptide.objects.count()} peptides, {Clinic.objects.count()} clinics, "
                f"{Review.objects.count()} reviews, {Post.objects.count()} posts."
            )
        )

    def _treatments(self):
        out = {}
        for order, row in enumerate(TREATMENTS):
            obj, _ = Treatment.objects.update_or_create(
                slug=slugify(row["name"]),
                defaults={**row, "sort_order": order},
            )
            out[obj.slug] = obj
        return out

    def _peptides(self, treatments):
        out = {}
        for row in PEPTIDES:
            data = dict(row)  # copy, so module-level data is never mutated
            treatment_slugs = data.pop("treatments")
            obj, _ = Peptide.objects.update_or_create(
                slug=slugify(data["name"]),
                defaults=data,
            )
            obj.treatments.set([treatments[slug] for slug in treatment_slugs])
            out[obj.slug] = obj
        return out

    def _protocols(self, treatments, peptides):
        for row in PROTOCOLS:
            obj, _ = Protocol.objects.update_or_create(
                slug=slugify(row["title"]),
                defaults={
                    "title": row["title"],
                    "treatment": treatments[row["treatment"]],
                    "summary": row["summary"],
                },
            )
            obj.peptides.set([peptides[slug] for slug in row["peptides"]])

    def _clinics(self, treatments, peptides):
        treatment_list = list(treatments.values())
        peptide_list = list(peptides.values())
        clinic_no = 0
        for state_row in GEO:
            state, _ = State.objects.update_or_create(
                slug=slugify(state_row["name"]),
                defaults={
                    "name": state_row["name"],
                    "abbreviation": state_row["abbreviation"],
                },
            )
            for city_row in state_row["cities"]:
                city, _ = City.objects.update_or_create(
                    state=state,
                    slug=slugify(city_row["name"]),
                    defaults={
                        "name": city_row["name"],
                        "latitude": city_row["latitude"],
                        "longitude": city_row["longitude"],
                    },
                )
                for n, suffix in enumerate(CLINIC_SUFFIXES):
                    name = f"Demo {city.name} {suffix}"
                    clinic, _ = Clinic.objects.update_or_create(
                        city=city,
                        slug=slugify(name),
                        defaults={
                            "name": name,
                            "address_line": "100 Example Street",
                            "postal_code": "00000",
                            "phone": f"(555) 010-0{clinic_no:02d}",
                            "website": "https://example.com",
                            "description": "Fictional demo clinic for development.",
                            "latitude": city.latitude + 0.01 * n,
                            "longitude": city.longitude + 0.01 * n,
                            "is_telehealth": n == 1,
                            "is_verified": n == 0,
                            "is_published": True,
                        },
                    )
                    clinic.treatments.set(
                        [treatment_list[(clinic_no + k) % len(treatment_list)] for k in range(3)]
                    )
                    for k in range(3):
                        ClinicPeptide.objects.update_or_create(
                            clinic=clinic,
                            peptide=peptide_list[(clinic_no + k) % len(peptide_list)],
                            defaults={
                                "price_from": Decimal(99 + 50 * k),
                                "price_note": "per month (demo)",
                            },
                        )
                    for review in REVIEWS:
                        Review.objects.get_or_create(
                            clinic=clinic,
                            author_name=review["author_name"],
                            defaults={
                                "rating": review["rating"],
                                "title": review["title"],
                                "body": "Demo review text.",
                                "is_approved": True,
                            },
                        )
                    clinic_no += 1

    def _posts(self, peptides):
        categories = {}
        for order, name in enumerate(CATEGORIES):
            category, _ = PostCategory.objects.get_or_create(
                slug=slugify(name),
                defaults={"name": name, "sort_order": order},
            )
            categories[name] = category
        for row in POSTS:
            post, _ = Post.objects.get_or_create(
                slug=slugify(row["title"]),
                defaults={
                    "title": row["title"],
                    "category": categories[row["category"]],
                    "excerpt": "Demo excerpt.",
                    "body": "Demo body text.",
                    "is_published": True,
                    "published_at": timezone.now(),
                },
            )
            post.peptides.set(list(peptides.values())[:2])