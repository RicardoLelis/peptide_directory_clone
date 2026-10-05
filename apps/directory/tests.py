import pytest
from django.core.management import call_command

from apps.directory.models import Clinic


@pytest.mark.django_db
def test_seed_is_idempotent_and_queryable():
    call_command("seed_demo")
    first_count = Clinic.objects.count()
    call_command("seed_demo")

    assert Clinic.objects.count() == first_count
    assert Clinic.objects.filter(
        city__state__slug="tennessee", peptides__slug="semaglutide"
    ).exists()