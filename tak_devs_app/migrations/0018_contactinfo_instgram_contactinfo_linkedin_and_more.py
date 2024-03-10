# Generated by Django 5.0.2 on 2024-03-10 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tak_devs_app', '0017_contactinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactinfo',
            name='instgram',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='contactinfo',
            name='linkedIn',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='contactinfo',
            name='skype',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='contactinfo',
            name='twitter',
            field=models.URLField(blank=True),
        ),
    ]
