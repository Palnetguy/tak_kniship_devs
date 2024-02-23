# Generated by Django 5.0.2 on 2024-02-23 09:53

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tak_devs_app', '0007_remove_gallery_photo_galleryimage_gallery_images'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gallery',
            name='images',
        ),
        migrations.AddField(
            model_name='gallery',
            name='photo',
            field=cloudinary.models.CloudinaryField(default='give', max_length=255, verbose_name='TAK/TAK_KNISHIP_DEVS/gallery_images'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='GalleryImage',
        ),
    ]
