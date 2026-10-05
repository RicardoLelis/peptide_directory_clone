from django.contrib import admin

from .models import Post, PostCategory


@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "published_at")
    list_filter = ("category", "is_published")
    search_fields = ("title",)
    list_select_related = ("category",)
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("peptides",)