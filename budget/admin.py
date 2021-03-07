from django.contrib import admin
from . import models


# Register your models here.
admin.site.register(models.Profile)


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at', 'user')
