from unittest.mock import Mock, patch
from types import SimpleNamespace

from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework.test import APIClient

from .models import ContactUsMessage
from .serializers import ContactUsMessageSerializer
from .signals import _deliver_contact_notifications, notify_admin_contact_form


class ContactNotificationDeliveryTests(SimpleTestCase):
    @override_settings(
        ADMIN_EMAILS=["first@example.com", "second@example.com"],
        RESEND_FROM_EMAIL="TAK Kinship Technologies <noreply@example.com>",
        ADMIN_SITE_URL="https://admin.example.com",
        PUBLIC_SITE_URL="https://example.com",
    )
    @patch("tak_devs_app.signals.render_to_string", return_value="<p>Email</p>")
    @patch("tak_devs_app.signals.email_executor.submit")
    def test_admin_recipients_are_sent_separate_messages(self, submit, _render):
        contact = SimpleNamespace(
            pk=42,
            email="visitor@example.com",
            subject="Hello",
        )

        notify_admin_contact_form(None, contact, created=True)

        messages = submit.call_args.args[1]
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0]["to"], ["first@example.com"])
        self.assertEqual(messages[1]["to"], ["second@example.com"])
        self.assertEqual(messages[2]["to"], ["visitor@example.com"])

    @override_settings(
        RESEND_API_KEY="test-key",
        EMAIL_TIMEOUT=10,
    )
    @patch("tak_devs_app.signals.requests.post")
    def test_delivers_each_message_through_resend(self, post):
        response = Mock()
        response.json.return_value = {"id": "email-id"}
        post.return_value = response
        messages = [{"from": "sender@example.com", "to": ["to@example.com"]}]

        _deliver_contact_notifications(messages, contact_message_id=42)

        post.assert_called_once_with(
            "https://api.resend.com/emails",
            headers={
                "Authorization": "Bearer test-key",
                "Content-Type": "application/json",
            },
            json=messages[0],
            timeout=10,
        )
        response.raise_for_status.assert_called_once_with()


class PublicContactSerializerTests(TestCase):
    @patch("tak_devs_app.signals.email_executor.submit")
    def test_public_submission_cannot_set_handling_fields(self, _submit):
        serializer = ContactUsMessageSerializer(data={
            "name": "Visitor",
            "subject": "Hello",
            "email": "visitor@example.com",
            "phone_number": "0700000000",
            "message": "Please contact me.",
            "handled_at": "2026-09-06T09:00:00Z",
            "handled_by": 1,
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        message = serializer.save()
        self.assertIsNone(message.handled_at)
        self.assertIsNone(message.handled_by)


class PublicContactSecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @override_settings(DEBUG=True)
    @patch("tak_devs_app.signals.email_executor.submit")
    def test_random_letter_submission_is_quarantined_without_email(self, submit):
        response = self.client.post(
            "/api/contact-us/",
            {
                "name": "Rlzjkkr Nnbmse",
                "subject": "Website enquiry from Hvmklcdry LLC",
                "email": "visitor@example.com",
                "message": "leEQugIdkxgTZiWeWaIdL",
            },
            format="json",
            HTTP_HOST="localhost",
            HTTP_X_TAK_CLIENT_IP="203.0.113.10",
            HTTP_X_TAK_USER_AGENT="security-test",
        )

        self.assertEqual(response.status_code, 201)
        message = ContactUsMessage.objects.get()
        self.assertTrue(message.is_spam)
        self.assertIn("random-letter-message", message.spam_reasons)
        self.assertNotEqual(message.source_ip_hash, "203.0.113.10")
        submit.assert_not_called()

    @override_settings(DEBUG=True)
    @patch("tak_devs_app.signals.email_executor.submit")
    def test_contact_email_has_a_daily_submission_limit(self, _submit):
        payload = {
            "name": "Genuine Visitor",
            "subject": "Project discussion",
            "email": "visitor@example.com",
            "message": "I would like to discuss a website project with your team.",
        }
        for index in range(3):
            response = self.client.post(
                "/api/contact-us/",
                {**payload, "message": f"{payload['message']} Reference {index}."},
                format="json",
                HTTP_HOST="localhost",
                HTTP_X_TAK_CLIENT_IP="203.0.113.11",
            )
            self.assertEqual(response.status_code, 201)

        limited = self.client.post(
            "/api/contact-us/",
            payload,
            format="json",
            HTTP_HOST="localhost",
            HTTP_X_TAK_CLIENT_IP="203.0.113.11",
        )
        self.assertEqual(limited.status_code, 429)
