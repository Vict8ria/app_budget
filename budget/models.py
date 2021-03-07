from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Project(models.Model):
    name = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_project'
    )

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse('project', args=[self.id])
