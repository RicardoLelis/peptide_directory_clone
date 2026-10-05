from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from apps.catalog.models import Peptide, Protocol, Treatment
from apps.content.models import Post, PostCategory
from apps.directory.models import City, Clinic, ClinicPeptide, Review, State

TREATMENTS = [  # (name, tagline, tint)
    ("Weight Loss", "Clinics offering medically supervised weight programs.", "mint"),
    ("Anti-Aging & Longevity", "Providers focused on healthy aging.", "peach"),
    ("Tissue Repair & Recovery", "Options aimed at injury recovery.", "rose"),
    ("Hormone Optimization", "Hormone-related protocols and providers.", "sky"),
    ("Cognitive Enhancement", "Focus and memory support options.", "lavender"),
    ("Sexual Wellness", "Clinically guided wellness options.", "peach"),
    ("Athletic Performance", "Strength, endurance and recovery.", "mint"),
    ("Immune Support", "Immune-related protocols.", "sky"),
]

PEPTIDES = [  # (name, status, class, summary, popular, treatment slugs)
    ("Semaglutide", "fda_approved", "GLP-1 Receptor Agonist",
     "Demo summary: GLP-1 medication profile.", True, ["weight-loss"]),
    ("Tirzepatide", "fda_approved", "GIP/GLP-1 Receptor Agonist",
     "Demo summary: dual-agonist medication profile.", True, ["weight-loss"]),
    ("BPC-157", "research_use", "Synthetic Fragment",
     "Demo summary: research-use compound profile.", True,
     ["tissue-repair-recovery", "athletic-performance"]),
    ("Retatrutide", "research_use", "Triple Incretin Agonist",
     "Demo summary: investigational compound profile.", True, ["weight-loss"]),
    ("Sermorelin", "compoundable", "Growth Hormone Releasing Hormone",
     "Demo summary: compounded peptide profile.", True,
     ["anti-aging-longevity", "hormone-optimization"]),
    ("CJC-1295 / Ipamorelin", "compoundable", "Growth Hormone Secretagogue",
     "Demo summary: secretagogue stack profile.", True,
     ["anti-aging-longevity", "athletic-performance"]),
]

PROTOCOLS = [  # (title, treatment slug, peptide slugs)
    ("Weight Loss & GLP-1 Overview", "weight-loss", ["semaglutide", "tirzepatide"]),
    ("Tissue Repair Overview", "tissue-repair-recovery", ["bpc-157"]),
]

GEO = {  # (state, abbreviation): [(city, lat, lng)]
    ("Tennessee", "TN"): [("Nashville", 36.1627, -86.7816), ("Memphis", 35.1495, -90.0490)],
    ("Texas", "TX"): [("Austin", 30.2672, -97.7431), ("Houston", 29.7604, -95.3698)],
    ("Florida", "FL"): [("Miami", 25.7617, -80.1918)],
    ("California", "CA"): [("Los Angeles", 34.0522, -118.2437)],
    ("New York", "NY"): [("New York", 40.7128, -74.0060)],
}

CLINIC_SUFFIXES = ["Wellness Clinic", "Peptide Medical Group"]

REVIEWS = [
    ("Demo Patient A", 5, "Clear and helpful", "Demo review text."),
    ("Demo Patient B", 4, "Good experience", "Demo review text."),
]

CATEGORIES = ["News", "How-To Guides", "Weight Loss Meds"]
POSTS = [  # (title, category)
    ("Demo news post", "News"),
    ("Demo how-to: reading a peptide profile", "How-To Guides"),
    ("Demo guide: questions to ask a clinic", "Weight Loss Meds"),
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
        for order, (name, tagline, tint) in enumerate(TREATMENTS):
            obj, _ = Treatment.objects.update_or_create(
                slug=slugify(name),
                defaults={"name": name, "tagline": tagline, "tint": tint, "sort_order": order},
            )
            out[obj.slug] = obj
        return out

    def _peptides(self, treatments):
        out = {}
        for name, status, drug_class, summary, popular, t_slugs in PEPTIDES:
            obj, _ = Peptide.objects.update_or_create(
                slug=slugify(name),
                defaults={
                    "name": name,
                    "regulatory_status": status,
                    "drug_class": drug_class,
                    "summary": summary,
                    "is_popular": popular,
                },
            )
            obj.treatments.set([treatments[s] for s in t_slugs])
            out[obj.slug] = obj
        return out

    def _protocols(self, treatments, peptides):
        for title, t_slug, p_slugs in PROTOCOLS:
            obj, _ = Protocol.objects.update_or_create(
                slug=slugify(title),
                defaults={
                    "title": title,
                    "treatment": treatments[t_slug],
                    "summary": "Demo protocol overview.",
                },
            )
            obj.peptides.set([peptides[s] for s in p_slugs])

    def _clinics(self, treatments, peptides):
        treatment_list = list(treatments.values())
        peptide_list = list(peptides.values())
        clinic_no = 0
        for (state_name, abbr), cities in GEO.items():
            state, _ = State.objects.update_or_create(
                slug=slugify(state_name), defaults={"name": state_name, "abbreviation": abbr}
            )
            for city_name, lat, lng in cities:
                city, _ = City.objects.update_or_create(
                    state=state,
                    slug=slugify(city_name),
                    defaults={"name": city_name, "latitude": lat, "longitude": lng},
                )
                for n, suffix in enumerate(CLINIC_SUFFIXES):
                    name = f"Demo {city_name} {suffix}"
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
                            "latitude": lat + 0.01 * n,
                            "longitude": lng + 0.01 * n,
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
                    for author, rating, title, body in REVIEWS:
                        Review.objects.get_or_create(
                            clinic=clinic,
                            author_name=author,
                            defaults={
                                "rating": rating,
                                "title": title,
                                "body": body,
                                "is_approved": True,
                            },
                        )
                    clinic_no += 1

    def _posts(self, peptides):
        categories = {}
        for order, name in enumerate(CATEGORIES):
            cat, _ = PostCategory.objects.get_or_create(
                slug=slugify(name), defaults={"name": name, "sort_order": order}
            )
            categories[name] = cat
        for title, cat_name in POSTS:
            post, _ = Post.objects.get_or_create(
                slug=slugify(title),
                defaults={
                    "title": title,
                    "category": categories[cat_name],
                    "excerpt": "Demo excerpt.",
                    "body": "Demo body text.",
                    "is_published": True,
                    "published_at": timezone.now(),
                },
            )
            post.peptides.set(list(peptides.values())[:2])