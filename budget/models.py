from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)


class Project(models.Model):
    name = models.CharField(max_length=60)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='projects'
    )

    def __str__(self):
        return self.name


class Transaction(models.Model):
    date = models.DateField()
    comment = models.CharField(max_length=200, blank=True)
    amount = models.CharField(max_length=10)
    transaction_type = models.CharField("Payment type", max_length=70)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions', unique=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='transactions', unique=False)

    def __str__(self):
        return self.amount
