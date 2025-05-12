from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Project, Agreement

# Define default policy text as constants
POLICY_DEFAULT_TEXT = """1. Information We Collect
We collect personal information such as your name, phone number, and usage data to provide and improve our services.

2. How We Use Your Information
We use your information to provide, maintain, and improve the app, as well as to communicate with you about our services.

3. Data Security
We implement appropriate technical and organizational measures to protect your personal information.

4. Sharing of Information
We do not sell or rent your personal information to third parties. We may share information with service providers who assist us in operating the app.

5. Children's Privacy
The app is suitable for users aged 6 and above. We do not knowingly collect personal information from children under 13 without parental consent.

6. Changes to This Policy
We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page.

7. Your Rights
You have the right to access, correct, or delete your personal information. Contact us if you wish to exercise these rights.

8. Contact Us
If you have any questions about this Privacy Policy, please contact us at info@takkinship.com."""

TERMS_DEFAULT_TEXT = """1. Acceptance of Terms
By using this application, you agree to be bound by these Terms of Service.

2. User Accounts
You are responsible for safeguarding your account and for any activities conducted through your account.

3. Prohibitions
You agree not to misuse the service or help anyone else do so.

4. Intellectual Property
The app and its contents are protected by copyright, trademark, and other laws.

5. Termination
We may terminate or suspend your access to the service at any time, without prior notice or liability.

6. Disclaimer
The app is provided "as is" without any warranties.

7. Limitation of Liability
To the maximum extent permitted by law, we shall not be liable for any indirect, incidental, special, consequential or punitive damages.

8. Governing Law
These Terms shall be governed by the laws of Uganda, without regard to its conflict of law provisions."""

@receiver(post_save, sender=Project)
def create_agreements(sender, instance, created, **kwargs):
    """
    Signal to automatically create Terms and Policy agreements when a new Project is created.
    """
    if created:
        # Create Policy agreement
        Agreement.objects.create(
            title=f"{instance.title} Privacy Policy",
            agreement_type="Policy",
            description=POLICY_DEFAULT_TEXT,
            project=instance,
            date_published=instance.date_published
        )
        
        # Create Terms agreement
        Agreement.objects.create(
            title=f"{instance.title} Terms of Service",
            agreement_type="Terms",
            description=TERMS_DEFAULT_TEXT,
            project=instance,
            date_published=instance.date_published
        )