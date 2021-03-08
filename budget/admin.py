from django.contrib import admin
from . import models


# Register your models here.
admin.site.register(models.Profile)


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at', 'owner')


@admin.register(models.Transaction)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('amount', 'date', 'comment', 'transaction_type', 'owner')
