# Generated by Django 4.0.2 on 2022-02-18 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0011_alter_countdown_view_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='countdown',
            name='result_photo',
            field=models.ImageField(default='resultlist.jpg', upload_to='results'),
        ),
    ]
