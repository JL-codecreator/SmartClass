# Generated by Django 4.0.8 on 2025-04-26 06:57

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('result', '0003_takencourse_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='takencourse',
            name='project',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5),
        ),
    ]
