# Generated by Django 4.0.2 on 2022-02-16 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0009_remove_countdown_start_time_counter'),
    ]

    operations = [
        migrations.AddField(
            model_name='countdown',
            name='title',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]
