# Generated by Django 4.0 on 2022-10-19 00:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='eth_wallet',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='trx_wallet',
        ),
    ]
