from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from admin_portal.models import ManagedProject, ProjectMembership, WebsiteContent
from tak_devs_app.models import (
    Agreement,
    ContactInfo,
    ContactUsMessage,
    DesktopApplication,
    FAQ,
    Gallery,
    MobileApplication,
    Project,
    ProjectClient,
    ProjectFeature,
    ProjectImage,
    TeamMember,
    TechStack,
    Testimonial,
    WebApplication,
    WorkExperience,
)


PLACEHOLDER_PATH = "seed/placeholder.svg"
PLACEHOLDER_SVG = b"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675">
<rect width="1200" height="675" fill="#08110d"/><circle cx="600" cy="290" r="110" fill="#2dbd72"/>
<text x="600" y="470" fill="#f4fff8" font-family="Arial,sans-serif" font-size="64" text-anchor="middle">TAK KINSHIP</text>
</svg>"""


class Command(BaseCommand):
    help = "Create deterministic sample data and a local super-admin account."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="localadmin")
        parser.add_argument("--email", default="localadmin@takkinship.test")
        parser.add_argument("--password", required=True)

    def handle(self, *args, **options):
        if not settings.DATABASES["default"]["ENGINE"].endswith("sqlite3"):
            raise CommandError("seed_local_dev is restricted to the local SQLite database.")

        password = options["password"]
        if len(password) < 12:
            raise CommandError("Use a local password containing at least 12 characters.")

        if not default_storage.exists(PLACEHOLDER_PATH):
            default_storage.save(PLACEHOLDER_PATH, ContentFile(PLACEHOLDER_SVG))

        user_model = get_user_model()
        admin, _ = user_model.objects.update_or_create(
            username=options["username"],
            defaults={
                "email": options["email"],
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        admin.set_password(password)
        admin.save(update_fields=["password"])

        managed_project, _ = ManagedProject.objects.update_or_create(
            slug="tak-kinship",
            defaults={
                "name": "TAK Kinship Technologies",
                "project_type": ManagedProject.ProjectType.WEBSITE,
                "status": ManagedProject.Status.ACTIVE,
                "description": "Public portfolio and company website.",
                "public_url": "http://localhost:3000",
                "repository_url": "https://github.com/Palnetguy/tak-kinship-portifolio",
                "module_key": "tak-kinship-website",
            },
        )
        ProjectMembership.objects.update_or_create(
            project=managed_project,
            user=admin,
            defaults={"role": ProjectMembership.Role.OWNER, "is_active": True},
        )

        WebsiteContent.objects.update_or_create(
            project=managed_project,
            key="home-hero",
            defaults={
                "value": {
                    "eyebrow": "TAK Kinship Technologies",
                    "heading": "Useful technology, built with care.",
                    "body": "Local seed content for testing the administration workflow.",
                    "primary_cta_label": "Explore our work",
                    "primary_cta_href": "/portfolio",
                },
                "is_published": True,
            },
        )

        stacks = {}
        for language in ("Next.js", "Django", "PostgreSQL", "Flutter", "Python"):
            stacks[language], _ = TechStack.objects.get_or_create(language=language)

        project_specs = (
            {
                "slug": "kinship-commerce",
                "title": "Kinship Commerce",
                "category": "Web Application",
                "stack": ("Next.js", "Django", "PostgreSQL"),
                "url": "https://example.com/kinship-commerce",
            },
            {
                "slug": "field-connect",
                "title": "Field Connect",
                "category": "Mobile App",
                "stack": ("Flutter", "Django"),
                "url": "https://example.com/field-connect.apk",
            },
            {
                "slug": "operations-desk",
                "title": "Operations Desk",
                "category": "Desktop Application",
                "stack": ("Python", "PostgreSQL"),
                "url": "https://example.com/operations-desk.exe",
            },
        )

        for index, spec in enumerate(project_specs, start=1):
            project, _ = Project.objects.update_or_create(
                slug=spec["slug"],
                defaults={
                    "title": spec["title"],
                    "project_category": spec["category"],
                    "quote": "Designed around people, reliability, and measurable results.",
                    "overview": "A complete sample project used to exercise portfolio and admin screens.",
                    "problem": "Teams needed a simpler and more dependable digital workflow.",
                    "solution": "TAK Kinship designed and delivered an accessible, maintainable product.",
                    "status": "Completed" if index < 3 else "In progress",
                    "about_project": "Representative local-development content with realistic relationships.",
                    "challenges_faced": "Connecting operational needs to a clear user experience.",
                    "date_published": date(2026, index, min(index * 6, 28)),
                    "duration_of_development": 8 + index * 3,
                    "is_published": True,
                },
            )
            project.tech_stack.set(stacks[name] for name in spec["stack"])
            ProjectFeature.objects.update_or_create(
                project=project,
                title="Responsive experience",
                defaults={"description": "Works clearly across desktop and mobile screens."},
            )
            ProjectFeature.objects.update_or_create(
                project=project,
                title="Secure administration",
                defaults={"description": "Role-aware tools keep content management controlled."},
            )
            ProjectImage.objects.update_or_create(
                project=project,
                image_type="background",
                defaults={"image": PLACEHOLDER_PATH, "caption": spec["title"], "order": 0},
            )

            client_defaults = {
                "name": f"Sample Client {index}",
                "location": "Kampala, Uganda",
                "rating": 5,
                "message": "The team turned a difficult workflow into a product people enjoy using.",
                "profile_image": PLACEHOLDER_PATH,
            }
            client = ProjectClient.objects.filter(project=project).first()
            if client:
                for field, value in client_defaults.items():
                    setattr(client, field, value)
                client.save(update_fields=list(client_defaults))
            else:
                ProjectClient.objects.bulk_create([ProjectClient(project=project, **client_defaults)])

            Agreement.objects.update_or_create(
                project=project,
                agreement_type="Policy",
                defaults={"title": f"{spec['title']} Privacy Policy", "description": "Sample privacy policy for local testing.", "date_published": date(2026, 1, 1)},
            )
            Agreement.objects.update_or_create(
                project=project,
                agreement_type="Terms",
                defaults={"title": f"{spec['title']} Terms", "description": "Sample terms for local testing.", "date_published": date(2026, 1, 1)},
            )

            if spec["category"] == "Web Application":
                WebApplication.objects.update_or_create(
                    project=project,
                    name=spec["title"],
                    defaults={"icon": PLACEHOLDER_PATH, "url": spec["url"]},
                )
            elif spec["category"] == "Mobile App":
                MobileApplication.objects.update_or_create(
                    project=project,
                    name=spec["title"],
                    defaults={"version": "1.0.0", "icon": PLACEHOLDER_PATH, "apk": None, "apk_url": spec["url"], "description": "Seed mobile download."},
                )
            else:
                DesktopApplication.objects.update_or_create(
                    project=project,
                    name=spec["title"],
                    defaults={"version": "1.0.0", "icon": PLACEHOLDER_PATH, "apk": None, "apk_url": spec["url"], "description": "Seed desktop download."},
                )

        faq_rows = (
            ("What does TAK Kinship build?", "We design and deliver web, mobile, desktop, and cloud products."),
            ("Can we begin with discovery?", "Yes. We can start by clarifying users, risks, scope, and delivery priorities."),
            ("Do you support products after launch?", "Yes. Support and iterative improvement can continue after release."),
        )
        for title, description in faq_rows:
            FAQ.objects.update_or_create(title=title, defaults={"description": description, "is_published": True})

        ContactInfo.objects.update_or_create(
            pk=1,
            defaults={
                "company_name": "TAK Kinship Technologies Limited",
                "location": "Kampala, Uganda",
                "email": "info@takkinship.test",
                "phone_number": "+256 700 000000",
                "instgram": "https://instagram.com/takkinship",
                "twitter": "https://x.com/takkinship",
                "skype": "",
                "linkedIn": "https://linkedin.com/company/takkinship",
            },
        )
        WorkExperience.objects.update_or_create(
            pk=1,
            defaults={"no_of_clients": 18, "no_of_complete_projects": 24, "years_of_experience": 7, "no_of_workers": 8, "desktop_dev": 70, "mobile_dev": 85, "web_dev": 92, "ui_dev": 88},
        )

        if not TeamMember.objects.filter(name="Amina Kato").exists():
            TeamMember.objects.bulk_create([
                TeamMember(profile_picture=PLACEHOLDER_PATH, name="Amina Kato", role="Product Designer", biography="Turns complex requirements into approachable experiences.", linkedin="https://linkedin.com", order=1, is_published=True),
                TeamMember(profile_picture=PLACEHOLDER_PATH, name="Daniel Okello", role="Software Engineer", biography="Builds dependable systems across frontend and backend.", linkedin="https://linkedin.com", order=2, is_published=True),
            ])
        if not Testimonial.objects.filter(name="Grace Namusoke").exists():
            Testimonial.objects.bulk_create([
                Testimonial(user_photo=PLACEHOLDER_PATH, name="Grace Namusoke", comment="TAK Kinship listened carefully and delivered a system our team can confidently use.", job_title="Operations Director", is_published=True),
                Testimonial(user_photo=PLACEHOLDER_PATH, name="Peter Mugisha", comment="Communication was clear and the product quality exceeded our expectations.", job_title="Founder", is_published=True),
            ])
        if not Gallery.objects.filter(image=PLACEHOLDER_PATH).exists():
            Gallery.objects.bulk_create([Gallery(image=PLACEHOLDER_PATH, is_published=True)])
        if not ContactUsMessage.objects.filter(email="prospect@example.test").exists():
            ContactUsMessage.objects.bulk_create([
                ContactUsMessage(name="Local Test Prospect", subject="Website redesign enquiry", email="prospect@example.test", phone_number="+256 700 111222", message="Please contact us about a new customer portal."),
            ])

        self.stdout.write(self.style.SUCCESS("Local development data is ready."))
        self.stdout.write(f"Admin login: {options['username']} / {password}")
