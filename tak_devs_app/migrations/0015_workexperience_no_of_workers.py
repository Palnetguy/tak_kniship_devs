# Generated by Django 5.0.2 on 2024-03-05 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tak_devs_app', '0014_desktopapplication_download_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='workexperience',
            name='no_of_workers',
            field=models.IntegerField(default=2),
        ),
    ]