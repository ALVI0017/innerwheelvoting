# Generated by Django 4.0.2 on 2022-02-11 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0003_alter_candidate_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='photo',
            field=models.ImageField(default='avatar.jpg', upload_to='candidates'),
        ),
    ]
