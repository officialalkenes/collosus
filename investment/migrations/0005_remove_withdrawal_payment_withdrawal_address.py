# Generated by Django 4.0 on 2022-10-19 00:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0004_withdrawal_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='withdrawal',
            name='payment',
        ),
        migrations.AddField(
            model_name='withdrawal',
            name='address',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Receiving Wallet Address'),
        ),
    ]
