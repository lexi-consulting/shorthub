# Generated by Django 5.1.2 on 2024-12-08 21:31

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TrainedModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("model_name", models.CharField(max_length=50)),
                ("coefficients", models.JSONField()),
                ("intercept", models.FloatField()),
            ],
        ),
    ]
