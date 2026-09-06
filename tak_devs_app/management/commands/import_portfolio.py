from datetime import date
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from tak_devs_app.models import Project, ProjectImage, TeamMember, TechStack


PROJECTS = (
    {
        "slug": "desn", "title": "Desn", "category": "Mobile App",
        "quote": "A shopping app that grew repeat orders for local vendors.",
        "overview": "Desn is a hyper-local commerce platform designed to bridge the gap between street vendors and digital-first customers in Mbarara.",
        "problem": "Local vendors lacked a reliable way to manage inventory and reach customers beyond physical foot traffic, leading to missed sales and inefficient stock management.",
        "solution": "TAK built a lightweight, offline-first mobile app that lets vendors track sales and stock in real time.",
        "status": "Live", "stack": ("Flutter", "Firebase"), "image": "desn.jpg", "published": date(2024, 1, 1),
    },
    {
        "slug": "stec-sms", "title": "STEC SMS", "category": "Desktop Application",
        "quote": "School management that cut admin time for staff.",
        "overview": "STEC SMS is a school management system built for administrative staff running day-to-day student and records operations.",
        "problem": "Staff were managing student records and admin tasks through manual, paper-based processes that were slow and error-prone.",
        "solution": "TAK built a desktop application with a Django and PostgreSQL backend and a Flutter client for day-to-day record keeping.",
        "status": "Completed", "stack": ("Python", "Django", "PostgreSQL", "Flutter"), "image": "stec-sms.jpg", "published": date(2024, 1, 1),
    },
    {
        "slug": "telxul", "title": "Telxul", "category": "Web Application",
        "quote": "Connecting different class cohorts from different schools in the country.",
        "overview": "Telxul is a web platform connecting class cohorts across different schools in the country.",
        "problem": "Students and cohorts from different schools had no shared platform to connect and collaborate with each other.",
        "solution": "TAK built a React and Django web app with a shared PostgreSQL backend so cohorts across schools can connect on one platform.",
        "status": "Completed", "stack": ("JavaScript", "HTML", "Python", "Django", "React", "PostgreSQL"), "image": "telxul.jpg", "published": date(2024, 1, 1),
    },
    {
        "slug": "projector23", "title": "Projector23", "category": "Mobile App",
        "quote": "A suite of four Flutter apps built for one client on a shared design system and backend.",
        "overview": "Projector23 is a suite of four Flutter apps built for one client on a shared design system and backend.",
        "problem": "The client needed four related apps to feel and behave consistently without building each one from scratch.",
        "solution": "TAK built a shared Flutter design system and backend, then shipped all four apps on top of it.",
        "status": "Completed", "stack": ("Flutter x4",), "image": "projector23.jpg", "published": date(2024, 1, 1),
    },
    {
        "slug": "tak-poultry-farm", "title": "TAK Poultry Farm", "category": "Mobile App",
        "quote": "A mobile app for a poultry operation, built for real-time flock and stock record keeping.",
        "overview": "A mobile app for a poultry operation, built for real-time flock and stock record keeping.",
        "problem": "The operation was tracking flock and stock records manually, with no shared, up-to-date view across staff.",
        "solution": "TAK built a Flutter app backed by Firebase so records update in real time across the team.",
        "status": "Completed", "stack": ("Flutter", "Firebase"), "image": "tak-poultry-farm.jpg", "published": date(2024, 1, 1),
    },
    {
        "slug": "tasse-fm", "title": "Tasse FM", "category": "Mobile App",
        "quote": "A media app for a radio station, pairing a Flutter client with a Django and PostgreSQL backend.",
        "overview": "A media app for a radio station, pairing a Flutter client with a Django and PostgreSQL backend.",
        "problem": "The station had no dedicated app for listeners, limiting how it could reach and engage its audience.",
        "solution": "TAK built a Flutter listener app on a Django and PostgreSQL backend, with Firebase for real-time features.",
        "status": "Completed", "stack": ("Flutter", "Firebase", "Python", "Django", "PostgreSQL"), "image": "tasse-fm.jpg", "published": date(2024, 1, 1),
    },
)

TEAM = (
    ("Tusingwire Martin", "Founder & Team Leader", "Building TAK Kinship has been the most rewarding work of my career. We stay small on purpose, because it keeps us close to the work and close to each other.", "martin.jpg"),
    ("Masaba Ian Samuel", "Head of Frontend", "I grew into leading our frontend work across web, desktop and mobile, turning half-formed ideas into interfaces that feel effortless.", "ian.jpg"),
    ("Yonah Odhiambo", "Backend Developer", "I build the reliable server-side systems our apps run on, mostly with Django, and care about doing that work well.", "yonah.jpg"),
    ("Fuad Michael Lawal", "UI/UX Designer", "I design systems the whole team can rely on, starting with a real problem before drawing a single screen.", "fuad.jpg"),
    ("Kazibwe David Nelson", "UI/UX Designer", "I design products that make a difference in our own communities, supported by honest feedback and genuine responsibility.", "david.jpg"),
    ("Lawrence Odhiambo", "Frontend Developer", "We work in fast, honest cycles, learning and adjusting as we go, with a real sense of ownership over what we ship.", "lawrence.jpg"),
)


class Command(BaseCommand):
    help = "Import the existing public portfolio into the local Django database and media storage."

    def add_arguments(self, parser):
        parser.add_argument("--source", required=True, help="Directory containing the existing portfolio image files.")
        parser.add_argument("--team-source", help="Directory containing the existing team image files.")

    def handle(self, *args, **options):
        source = Path(options["source"])
        if not source.is_dir():
            raise CommandError(f"Image source does not exist: {source}")

        imported = 0
        for item in PROJECTS:
            project, _ = Project.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "title": item["title"], "project_category": item["category"], "quote": item["quote"],
                    "overview": item["overview"], "problem": item["problem"], "solution": item["solution"],
                    "status": item["status"], "about_project": item["overview"], "challenges_faced": item["problem"],
                    "date_published": item["published"], "duration_of_development": 0, "is_published": True,
                },
            )
            project.tech_stack.set([TechStack.objects.get_or_create(language=name)[0] for name in item["stack"]])

            image_path = source / item["image"]
            if not image_path.is_file():
                raise CommandError(f"Missing image for {project.title}: {image_path}")
            image, created = ProjectImage.objects.get_or_create(project=project, image_type="background", defaults={"order": 0})
            if created or not image.image:
                with image_path.open("rb") as handle:
                    image.image.save(image_path.name, File(handle), save=True)
            imported += 1
            self.stdout.write(self.style.SUCCESS(f"Imported {project.title}"))

        self.stdout.write(self.style.SUCCESS(f"Imported {imported} portfolio projects into local media storage."))

        team_source_value = options.get("team_source")
        if not team_source_value:
            return
        team_source = Path(team_source_value)
        if not team_source.is_dir():
            raise CommandError(f"Team image source does not exist: {team_source}")
        for order, (name, role, biography, filename) in enumerate(TEAM):
            member, _ = TeamMember.objects.update_or_create(
                name=name,
                defaults={"role": role, "biography": biography, "linkedin": "", "order": order, "is_published": True},
            )
            image_path = team_source / filename
            if not image_path.is_file():
                raise CommandError(f"Missing image for {member.name}: {image_path}")
            if not member.profile_picture:
                with image_path.open("rb") as handle:
                    member.profile_picture.save(image_path.name, File(handle), save=True)
            self.stdout.write(self.style.SUCCESS(f"Imported {member.name}"))
