from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


def _build_unique_slug(model_class, value, instance_pk=None):
    base_slug = slugify(value)[:50] or "item"
    slug = base_slug
    counter = 2

    while True:
        queryset = model_class.objects.filter(slug=slug)
        if instance_pk:
            queryset = queryset.exclude(pk=instance_pk)
        if not queryset.exists():
            return slug
        suffix = f"-{counter}"
        slug = f"{base_slug[:50-len(suffix)]}{suffix}"
        counter += 1


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _build_unique_slug(Category, self.name, self.pk)
        super().save(*args, **kwargs)


class Product(models.Model):
    categories = models.ManyToManyField(Category, related_name="products")
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    stock = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _build_unique_slug(Product, self.name, self.pk)
        super().save(*args, **kwargs)
