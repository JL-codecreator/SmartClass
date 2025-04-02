# Generated by Django 4.2.16 on 2024-09-29 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_newsandevents_summary_en_newsandevents_summary_ru_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="newsandevents",
            name="summary_es",
            field=models.TextField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="newsandevents",
            name="summary_fr",
            field=models.TextField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="newsandevents",
            name="title_es",
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="newsandevents",
            name="title_fr",
            field=models.CharField(max_length=200, null=True),
        ),
    ]
