from django.db import migrations


def register_tak_kinship(apps, schema_editor):
    ManagedProject = apps.get_model("admin_portal", "ManagedProject")
    ManagedProject.objects.get_or_create(
        slug="tak-kinship",
        defaults={
            "name": "TAK Kinship",
            "project_type": "website",
            "status": "active",
            "description": "The public TAK Kinship website and its administration module.",
            "public_url": "https://takkinship.com",
            "module_key": "tak-kinship-website",
        },
    )


def unregister_tak_kinship(apps, schema_editor):
    ManagedProject = apps.get_model("admin_portal", "ManagedProject")
    ManagedProject.objects.filter(slug="tak-kinship").delete()


class Migration(migrations.Migration):
    dependencies = [("admin_portal", "0001_initial")]

    operations = [migrations.RunPython(register_tak_kinship, unregister_tak_kinship)]
