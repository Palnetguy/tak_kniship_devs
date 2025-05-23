# Generated by Django 5.0.2 on 2025-05-11 13:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tak_devs_app', '0027_remove_project_project_background_image_projectimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectimage',
            name='caption',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='projectimage',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='projectimage',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='tak_devs_app.project'),
        ),
    ]
