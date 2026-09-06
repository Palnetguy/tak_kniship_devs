from django.conf import settings
from django.db import migrations


def assign_existing_staff(apps, schema_editor):
    ManagedProject = apps.get_model("admin_portal", "ManagedProject")
    ProjectMembership = apps.get_model("admin_portal", "ProjectMembership")
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))

    project = ManagedProject.objects.filter(slug="tak-kinship").first()
    if not project:
        return

    for user in User.objects.filter(is_staff=True, is_active=True):
        ProjectMembership.objects.get_or_create(
            project=project,
            user=user,
            defaults={"role": "admin", "is_active": True},
        )


class Migration(migrations.Migration):
    dependencies = [("admin_portal", "0004_seed_home_hero_content")]

    operations = [
        migrations.RunPython(assign_existing_staff, migrations.RunPython.noop),
    ]
