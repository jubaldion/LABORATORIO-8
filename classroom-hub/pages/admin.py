from django.contrib import admin

from .models import Category, Resource


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "available", "created_at")
    list_filter = ("available", "category")
    search_fields = ("title", "description", "category__name")
    list_select_related = ("category",)
    list_per_page = 20