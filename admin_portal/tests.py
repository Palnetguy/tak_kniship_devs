from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import AuditEvent, ManagedProject
from tak_devs_app.models import ContactUsMessage, FAQ


class AdminPortalApiTests(TestCase):
    def setUp(self):
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
