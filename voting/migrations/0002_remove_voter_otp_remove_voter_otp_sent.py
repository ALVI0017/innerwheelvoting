# Generated by Django 4.0.2 on 2022-02-10 21:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='voter',
            name='otp',
        ),
        migrations.RemoveField(
            model_name='voter',
            name='otp_sent',
        ),
    ]
