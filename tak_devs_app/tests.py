from unittest.mock import Mock, patch
from types import SimpleNamespace

from django.test import SimpleTestCase, override_settings

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
