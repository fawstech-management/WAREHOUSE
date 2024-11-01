# Generated by Django 5.0 on 2024-10-21 10:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0025_ordernotification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingdetail',
            name='phone',
            field=models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(message='Phone number must be entered in the format, eg: +918541744560. Up to 15 digits allowed.', regex='^\\+?\\d{9,15}$')]),
        ),
    ]
