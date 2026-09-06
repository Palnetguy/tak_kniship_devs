from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("admin_portal", "0002_register_tak_kinship")]
    operations = [
        migrations.CreateModel(
            name="WebsiteContent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.SlugField()), ("value", models.JSONField(default=dict)),
                ("is_published", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
                ("project", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="website_content", to="admin_portal.managedproject")),
            ],
            options={"ordering": ["key"]},
        ),
        migrations.AddConstraint(model_name="websitecontent", constraint=models.UniqueConstraint(fields=("project", "key"), name="unique_website_content_key")),
    ]
