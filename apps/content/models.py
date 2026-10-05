from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


class PostCategory(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "post categories"

    def __str__(self):
        return self.name


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True, published_at__lte=timezone.now())


class Post(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=210, unique=True)
    category = models.ForeignKey(PostCategory, on_delete=models.PROTECT, related_name="posts")
    excerpt = models.CharField(max_length=300, blank=True)
    body = models.TextField()
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    # Blog-to-entity links feed the internal-linking strategy (Phase 7).
    peptides = models.ManyToManyField("catalog.Peptide", related_name="posts", blank=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title