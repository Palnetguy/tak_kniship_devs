from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Project, Agreement, Testimonial, ProjectClient

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

@receiver(post_save, sender=Testimonial)
def notify_new_testimonial(sender, instance, created, **kwargs):
    """Send email notification when a new testimonial is submitted"""
    if created:
        subject = f"New Testimonial Received from {instance.name}"
        
        plain_message = f"""
New testimonial submitted!

From: {instance.name} ({instance.job_title})
Comment: {instance.comment}

You can view this testimonial in the admin panel:
{settings.SITE_URL}/admin/tak_devs_app/testimonial/{instance.pk}/change/
        """
        
        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #1fa84f; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f9f9f9; border-radius: 4px; }}
        .testimonial {{ background: #fff; padding: 15px; border-left: 4px solid #1fa84f; margin: 20px 0; }}
        .button {{ display: inline-block; background: #1fa84f; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>New Testimonial Received!</h1>
        </div>
        <div class="content">
            <p>A new testimonial has been submitted to your website:</p>
            
            <div class="testimonial">
                <h3>{instance.name}</h3>
                <p><em>{instance.job_title}</em></p>
                <blockquote>"{instance.comment}"</blockquote>
            </div>
            
            <p>You can review this testimonial in your admin panel.</p>
            <p><a href="{settings.SITE_URL}/admin/tak_devs_app/testimonial/{instance.pk}/change/" class="button">View in Admin</a></p>
        </div>
    </div>
</body>
</html>
        """
        
        send_mail(
            subject,
            plain_message,
            settings.EMAIL_HOST_USER,
            [settings.ADMIN_EMAIL],  # Add this to your settings.py
            html_message=html_message,
            fail_silently=False,
        )

@receiver(post_save, sender=ProjectClient)
def notify_new_feedback(sender, instance, created, **kwargs):
    """Send email notification when new client feedback is submitted"""
    if created:
        subject = f"New Client Feedback for {instance.project.title}"
        
        stars = "★" * instance.rating + "☆" * (5 - instance.rating)
        
        plain_message = f"""
New client feedback submitted!

Project: {instance.project.title}
From: {instance.name} ({instance.location})
Rating: {instance.rating}/5
Message: {instance.message}

You can view this feedback in the admin panel:
{settings.SITE_URL}/admin/tak_devs_app/projectclient/{instance.pk}/change/
        """
        
        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #1fa84f; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f9f9f9; border-radius: 4px; }}
        .feedback {{ background: #fff; padding: 15px; border-left: 4px solid #1fa84f; margin: 20px 0; }}
        .project {{ border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 10px; }}
        .stars {{ color: #1fa84f; font-size: 24px; }}
        .button {{ display: inline-block; background: #1fa84f; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>New Client Feedback Received!</h1>
        </div>
        <div class="content">
            <div class="feedback">
                <div class="project">
                    <h2>{instance.project.title}</h2>
                </div>
                
                <p><strong>From:</strong> {instance.name} ({instance.location})</p>
                
                <p><strong>Rating:</strong> <span class="stars">{stars}</span> {instance.rating}/5</p>
                
                <blockquote>"{instance.message}"</blockquote>
            </div>
            
            <p>You can view the complete feedback details in your admin panel.</p>
            <p><a href="{settings.SITE_URL}/admin/tak_devs_app/projectclient/{instance.pk}/change/" class="button">View in Admin</a></p>
        </div>
    </div>
</body>
</html>
        """
        
        send_mail(
            subject,
            plain_message,
            settings.EMAIL_HOST_USER,
            [settings.ADMIN_EMAIL],  # Add this to your settings.py 
            html_message=html_message,
            fail_silently=False,
        )

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