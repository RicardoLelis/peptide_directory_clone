from django.contrib import admin

from .models import City, Clinic, ClinicPeptide, Review, State


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ("name", "abbreviation")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "state")
    list_filter = ("state",)
    search_fields = ("name",)
    list_select_related = ("state",)
    prepopulated_fields = {"slug": ("name",)}


class ClinicPeptideInline(admin.TabularInline):
    model = ClinicPeptide
    extra = 1
    autocomplete_fields = ("peptide",)


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "is_telehealth", "is_verified", "is_published")
    list_filter = ("is_published", "is_verified", "is_telehealth", "city__state")
    search_fields = ("name", "city__name")
    list_select_related = ("city__state",)
    autocomplete_fields = ("city",)
    filter_horizontal = ("treatments",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ClinicPeptideInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("clinic", "author_name", "rating", "is_approved", "created_at")
    list_filter = ("is_approved", "rating")
    list_editable = ("is_approved",)
    list_select_related = ("clinic",)