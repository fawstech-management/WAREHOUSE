# Generated by Django 5.1.2 on 2024-10-28 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0031_alter_order_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('processed', 'Processed'), ('shipped', 'Shipped'), ('delivered', 'Delivered')], default='pending', max_length=20),
        ),
    ]
