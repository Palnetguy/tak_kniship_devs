# Generated by Django 5.0.2 on 2024-02-11 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tak_devs_app', '0002_alter_mobileapplication_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='desktopapplication',
            name='url',
            field=models.URLField(blank=True),
        ),
    ]
