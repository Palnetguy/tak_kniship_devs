# Generated by Django 5.0.2 on 2025-05-10 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tak_devs_app', '0021_rename_type_agreement_agreement_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teammember',
            name='skype',
        ),
        migrations.AddField(
            model_name='teammember',
            name='biography',
            field=models.TextField(blank=True),
        ),
    ]
