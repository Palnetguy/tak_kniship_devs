from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings

from .signals import _deliver_contact_notifications


class ContactNotificationDeliveryTests(SimpleTestCase):
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
