# Generated by Django 4.0 on 2022-10-18 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='deposit',
            name='slug',
            field=models.SlugField(blank=True, max_length=8),
        ),
    ]
