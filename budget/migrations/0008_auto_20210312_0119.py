# Generated by Django 3.1.7 on 2021-03-11 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0007_auto_20210309_0140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='comment',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(max_length=70, verbose_name='Payment type'),
        ),
    ]
