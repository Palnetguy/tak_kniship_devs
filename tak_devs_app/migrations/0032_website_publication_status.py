from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("tak_devs_app", "0031_contactusmessage_handling")]

    operations = [
        migrations.AddField(model_name="project", name="is_published", field=models.BooleanField(default=True)),
        migrations.AddField(model_name="teammember", name="is_published", field=models.BooleanField(default=True)),
        migrations.AddField(model_name="testimonial", name="is_published", field=models.BooleanField(default=True)),
        migrations.AddField(model_name="gallery", name="is_published", field=models.BooleanField(default=True)),
        migrations.AddField(model_name="faq", name="is_published", field=models.BooleanField(default=True)),
    ]
