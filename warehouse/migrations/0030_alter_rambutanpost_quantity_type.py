# Generated by Django 5.1.2 on 2024-10-27 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0029_rambutanpost_category_alter_rambutanpost_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rambutanpost',
            name='quantity_type',
            field=models.CharField(choices=[('kg', 'Kilograms'), ('L', 'Litres')], max_length=10),
        ),
    ]
