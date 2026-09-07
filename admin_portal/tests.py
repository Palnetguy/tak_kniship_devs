from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import AuditEvent, ContactMessageReply, ManagedProject, ProjectMembership
from tak_devs_app.models import Agreement, ContactUsMessage, FAQ, Project, ProjectImage
from tak_devs_app.views import generate_client_feedback_link


class AdminPortalApiTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="tak-admin",
            password="safe-test-password",
            is_staff=True,
        )
        self.project = ManagedProject.objects.create(
            slug="test-platform",
            name="Test platform",
            project_type=ManagedProject.ProjectType.API,
            module_key="test-platform-api",
        )
        website_project, _ = ManagedProject.objects.get_or_create(
            slug="tak-kinship",
            defaults={
                "name": "TAK Kinship",
                "project_type": ManagedProject.ProjectType.WEBSITE,
                "module_key": "tak-kinship-website",
            },
        )
        ProjectMembership.objects.create(
            project=self.project,
            user=self.user,
            role=ProjectMembership.Role.ADMIN,
        )
        ProjectMembership.objects.get_or_create(
            project=website_project,
            user=self.user,
            defaults={"role": ProjectMembership.Role.ADMIN},
        )

    def test_dashboard_requires_a_staff_session(self):
        response = self.client.get("/api/admin/v1/dashboard/")
        self.assertEqual(response.status_code, 403)

    def test_staff_member_can_read_dashboard_and_projects(self):
        self.client.force_login(self.user)

        dashboard = self.client.get("/api/admin/v1/dashboard/")
        projects = self.client.get("/api/admin/v1/projects/")

        self.assertEqual(dashboard.status_code, 200)
        self.assertGreaterEqual(dashboard.data["summary"]["projects"], 1)
        self.assertEqual(projects.status_code, 200)
        self.assertIn(
            self.project.slug,
            [project["slug"] for project in projects.data["projects"]],
        )

    def test_staff_member_can_read_the_website_module_overview(self):
        self.client.force_login(self.user)
        response = self.client.get("/api/admin/v1/website/overview/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("open_enquiries", response.data["summary"])

    def test_login_creates_an_audit_event(self):
        self.client.get("/api/admin/v1/auth/csrf/")
        response = self.client.post(
            "/api/admin/v1/auth/login/",
            {"username": "tak-admin", "password": "safe-test-password"},
            format="json",
            HTTP_X_CSRFTOKEN=self.client.cookies["csrftoken"].value,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"]["username"], "tak-admin")
        self.assertTrue(AuditEvent.objects.filter(action="admin.auth.signed_in").exists())

    def test_login_attempts_are_rate_limited(self):
        self.client.get("/api/admin/v1/auth/csrf/")
        csrf_token = self.client.cookies["csrftoken"].value
        responses = [
            self.client.post(
                "/api/admin/v1/auth/login/",
                {"username": "tak-admin", "password": "wrong-password"},
                format="json",
                HTTP_X_CSRFTOKEN=csrf_token,
            )
            for _ in range(11)
        ]

        self.assertEqual(responses[-1].status_code, 429)

    def test_staff_member_can_manage_faqs_and_records_the_change(self):
        self.client.force_login(self.user)
        response = self.client.post(
            "/api/admin/v1/faqs/",
            {"title": "How do we begin?", "description": "Start with a conversation."},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(FAQ.objects.filter(title="How do we begin?").exists())
        self.assertTrue(AuditEvent.objects.filter(action="admin.faqs.created").exists())

    def test_viewer_cannot_change_website_content(self):
        ProjectMembership.objects.filter(
            project__slug="tak-kinship",
            user=self.user,
        ).update(role=ProjectMembership.Role.VIEWER)
        self.client.force_login(self.user)

        response = self.client.post(
            "/api/admin/v1/faqs/",
            {"title": "Restricted", "description": "Must not be created."},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(FAQ.objects.filter(title="Restricted").exists())

    def test_staff_member_can_mark_a_contact_message_handled(self):
        message = ContactUsMessage.objects.create(
            name="A client",
            subject="Website enquiry",
            email="client@example.com",
            message="I would like to work with TAK.",
            phone_number="0700000000",
        )
        self.client.force_login(self.user)
        response = self.client.patch(
            f"/api/admin/v1/messages/{message.id}/",
            {"handled_at": "2026-09-06T09:00:00Z"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        message.refresh_from_db()
        self.assertEqual(message.handled_by, self.user)
        self.assertIsNotNone(message.handled_at)

    def test_staff_member_can_reply_to_a_contact_message_in_local_preview(self):
        message = ContactUsMessage.objects.create(
            name="A client",
            subject="Website enquiry",
            email="client@example.com",
            message="Can you help?",
            phone_number="0700000000",
        )
        self.client.force_login(self.user)
        with self.settings(DEBUG=True, RESEND_API_KEY=""):
            response = self.client.post(
                f"/api/admin/v1/messages/{message.id}/reply/",
                {"subject": "Re: Website enquiry", "body": "Yes, we would be glad to help."},
                format="json",
            )

        self.assertEqual(response.status_code, 200)
        reply = ContactMessageReply.objects.get(contact_message=message)
        self.assertEqual(reply.delivery_mode, "local-preview")
        message.refresh_from_db()
        self.assertIsNotNone(message.handled_at)

    def test_staff_member_can_manage_agreements(self):
        project = Project.objects.create(
            title="Test project",
            slug="test-project",
            project_category="Web Application",
            about_project="Test",
            date_published="2026-09-07",
            duration_of_development=2,
        )
        self.client.force_login(self.user)
        response = self.client.post(
            "/api/admin/v1/agreements/",
            {
                "project": project.pk,
                "title": "Privacy policy",
                "agreement_type": "Policy",
                "description": "Test policy",
                "date_published": "2026-09-07",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Agreement.objects.filter(project=project).exists())

    def test_staff_member_can_upload_a_project_cover_image(self):
        project = Project.objects.create(
            title="Image project",
            slug="image-project",
            project_category="Web Application",
            about_project="Test",
            date_published="2026-09-07",
            duration_of_development=2,
        )
        image = SimpleUploadedFile(
            "cover.gif",
            b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
            content_type="image/gif",
        )
        self.client.force_login(self.user)
        response = self.client.post(
            "/api/admin/v1/project-images/",
            {"project": project.pk, "image": image, "image_type": "background", "order": 0},
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(ProjectImage.objects.filter(project=project, image_type="background").exists())

    def test_feedback_request_is_prepared_in_local_development(self):
        project = Project.objects.create(
            title="Feedback project",
            slug="feedback-project",
            project_category="Web Application",
            about_project="Test",
            date_published="2026-09-07",
            duration_of_development=2,
        )
        self.client.force_login(self.user)
        with self.settings(DEBUG=True, RESEND_API_KEY=""):
            response = self.client.post(
                f"/api/admin/v1/portfolio/{project.pk}/request-feedback/",
                {"recipient_name": "Test Client", "recipient_email": "client@example.com"},
                format="json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["delivery_mode"], "local-preview")

    def test_client_can_submit_and_update_feedback_from_signed_link(self):
        project = Project.objects.create(
            title="Feedback form project",
            slug="feedback-form-project",
            project_category="Web Application",
            about_project="Test",
            date_published="2026-09-07",
            duration_of_development=2,
        )
        token = generate_client_feedback_link(project)
        url = reverse(
            "client_feedback_form",
            kwargs={"project_id": project.pk, "token": token},
        )

        self.assertEqual(self.client.get(url).status_code, 200)
        first = self.client.post(
            url,
            {"name": "Test Client", "location": "Kampala", "rating": 5, "message": "Excellent work."},
        )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(project.client.message, "Excellent work.")

        updated = self.client.post(
            url,
            {"name": "Test Client", "location": "Mbarara", "rating": 4, "message": "Updated feedback."},
        )
        self.assertEqual(updated.status_code, 200)
        project.client.refresh_from_db()
        self.assertEqual(project.client.message, "Updated feedback.")

    def test_platform_owner_can_create_and_update_an_admin_account(self):
        self.user.is_superuser = True
        self.user.save(update_fields=["is_superuser"])
        self.client.force_login(self.user)
        created = self.client.post(
            "/api/admin/v1/accounts/",
            {"username": "content-editor", "email": "editor@example.com", "password": "a-secure-test-password"},
            format="json",
        )
        self.assertEqual(created.status_code, 201)
        updated = self.client.patch(
            f"/api/admin/v1/accounts/{created.data['account']['id']}/",
            {"first_name": "Content", "is_active": False},
            format="json",
        )
        self.assertEqual(updated.status_code, 200)
        self.assertFalse(updated.data["account"]["is_active"])
