from django.contrib import admin

from .models import Peptide, Protocol, Treatment


@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ("name", "tint", "sort_order")
    list_editable = ("sort_order",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Peptide)
class PeptideAdmin(admin.ModelAdmin):
    list_display = ("name", "regulatory_status", "drug_class", "is_popular")
    list_filter = ("regulatory_status", "is_popular", "treatments")
    search_fields = ("name", "drug_class")   # also required by autocomplete_fields elsewhere
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("treatments",)


@admin.register(Protocol)
class ProtocolAdmin(admin.ModelAdmin):
    list_display = ("title", "treatment")
    list_filter = ("treatment",)
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("peptides",)