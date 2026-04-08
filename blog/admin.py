from django.contrib import admin
from .models import MushroomDetail, MushroomPhoto


class MushroomPhotoInline(admin.TabularInline):
    model = MushroomPhoto
    extra = 4


class MushroomDetailAdmin(admin.ModelAdmin):
    inlines = [MushroomPhotoInline]
    list_display = ('title', 'latin_name', 'date')


admin.site.register(MushroomDetail, MushroomDetailAdmin)
