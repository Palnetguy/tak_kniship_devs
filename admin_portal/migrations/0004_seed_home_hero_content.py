from django.db import migrations


def seed_home_hero(apps, schema_editor):
    Project = apps.get_model("admin_portal", "ManagedProject")
    WebsiteContent = apps.get_model("admin_portal", "WebsiteContent")
    project = Project.objects.get(slug="tak-kinship")
    WebsiteContent.objects.get_or_create(
        project=project,
        key="home-hero",
        defaults={
            "is_published": True,
            "value": {
                "heading": "Where innovation meets impact.",
                "body": "We turn bold ideas into impactful digital solutions. At TAK Kinship, we engineer robust software, craft intuitive experiences, and build scalable infrastructure for modern enterprises.",
                "primary_cta_label": "Start a Project",
                "primary_cta_href": "/contact",
                "secondary_cta_label": "See Our Work",
                "secondary_cta_href": "/portfolio",
            },
        },
    )


class Migration(migrations.Migration):
    dependencies = [("admin_portal", "0003_websitecontent")]
    operations = [migrations.RunPython(seed_home_hero, migrations.RunPython.noop)]
