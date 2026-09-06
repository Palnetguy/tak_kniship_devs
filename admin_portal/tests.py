from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import AuditEvent, ManagedProject


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
