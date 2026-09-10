# views.py
from datetime import timedelta
import hashlib
import hmac
import ipaddress
import re

from django.shortcuts import get_object_or_404, render, redirect
from rest_framework import generics
from rest_framework.exceptions import Throttled

from tak_web.settings import EMAIL_HOST_USER
from .models import Agreement, ContactInfo, FeedbackInvitation, Project, ProjectClient, TeamMember, Testimonial, Gallery, FAQ, ContactUsMessage, WorkExperience, MobileApplication, DesktopApplication, WebApplication
from .serializers import AgreementSerializer, ContactInfoSeriliazer, ProjectSerializer, TeamMemberSerializer, TestimonialSerializer, GallerySerializer, FAQSerializer, ContactUsMessageSerializer, WorkExperienceSerializer, MobileApplicationSerializer, DesktopApplicationSerializer, WebApplicationSerializer
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework_api_key.permissions import HasAPIKey
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from drf_yasg.utils import swagger_auto_schema
from django.contrib import messages
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from .forms import TestimonialForm, ProjectClientFeedbackForm
from django.conf import settings
from django.utils import timezone

from django.http import HttpResponse
import requests


class LocalOrHasAPIKey(BasePermission):
    """Keep production public APIs key-protected while supporting local site preview."""

    def has_permission(self, request, view):
        host = request.get_host().split(":")[0]
        return bool(settings.DEBUG and host in {"127.0.0.1", "localhost"}) or HasAPIKey().has_permission(request, view)


def health_check(request):
    return HttpResponse("OK", status=200)

class ProjectListView(generics.ListAPIView):
    """
    Lists all projects with their features, tech stack, and client information.
    """
    queryset = (
        Project.objects.filter(is_published=True)
        .exclude(slug="")
        .select_related('client')
        .prefetch_related(
            'tech_stack', 'images', 'features', 'mobile_applications',
            'desktop_applications', 'web_applications',
        )
    )
    serializer_class = ProjectSerializer
    permission_classes = [LocalOrHasAPIKey]

    @swagger_auto_schema(
        operation_description="Get a list of all projects",
        responses={200: ProjectSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ProjectDetailView(generics.RetrieveAPIView):
    """
    Retrieves details for a specific project.
    """
    queryset = ProjectListView.queryset
    serializer_class = ProjectSerializer
    permission_classes = [LocalOrHasAPIKey]

    @swagger_auto_schema(
        operation_description="Get details of a specific project",
        responses={200: ProjectSerializer()}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ProjectDetailWithApplicationsView(generics.RetrieveAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [LocalOrHasAPIKey]

    def get_queryset(self):
        return Project.objects.filter(is_published=True).exclude(slug="").select_related('client').prefetch_related(
            'tech_stack',
            'images',
            'features',
            'mobile_applications',  # Changed from mobileapplication_set
            'desktop_applications',  # Changed from desktopapplication_set
            'web_applications',     # Changed from webapplication_set
            'features',            # Added features
            'client'              # Added client
        )

    
class PolicyDetailAgreement(generics.RetrieveAPIView):
    # queryset = Agreement.objects.all()
    serializer_class = AgreementSerializer
    permission_classes = [LocalOrHasAPIKey]

    # def get_queryset(self):
    #     project_id = self.kwargs.get('project_id')
    #     return Agreement.objects.filter(project__id=project_id, agreement_type='Policy' )
    
    def get_object(self):
        project_id = self.kwargs.get('project_id')
        return get_object_or_404(Agreement, project__id=project_id, agreement_type='Policy')
    
class TermsDetailAgreement(generics.RetrieveAPIView):
    serializer_class = AgreementSerializer
    permission_classes = [LocalOrHasAPIKey]

    def get_object(self):
        project_id = self.kwargs.get('project_id')
        return get_object_or_404(Agreement, project__id=project_id, agreement_type='Terms')
   


class TeamMemberListView(generics.ListAPIView):
    serializer_class = TeamMemberSerializer
    permission_classes = [LocalOrHasAPIKey]
    
    def get_queryset(self):
        # Explicitly order by 'order' field and then by 'name'
        return TeamMember.objects.filter(is_published=True).order_by('order', 'name')

class TestimonialListView(generics.ListAPIView):
    queryset = Testimonial.objects.filter(is_published=True)
    serializer_class = TestimonialSerializer
    permission_classes = [LocalOrHasAPIKey]

class GalleryListView(generics.ListAPIView):
    queryset = Gallery.objects.filter(is_published=True)
    serializer_class = GallerySerializer
    permission_classes = [LocalOrHasAPIKey]

class FAQListView(generics.ListAPIView):
    queryset = FAQ.objects.filter(is_published=True)
    serializer_class = FAQSerializer
    permission_classes = [LocalOrHasAPIKey]



class ContactUsMessageCreateView(generics.CreateAPIView):
    queryset = ContactUsMessage.objects.all()
    serializer_class = ContactUsMessageSerializer
    permission_classes = [LocalOrHasAPIKey]

    def perform_create(self, serializer):
        now = timezone.now()
        email = serializer.validated_data['email'].strip().lower()
        message = serializer.validated_data['message'].strip()
        client_ip = self.request.headers.get('X-TAK-Client-IP', '').strip()
        try:
            client_ip = str(ipaddress.ip_address(client_ip))
        except ValueError:
            client_ip = ''

        def private_hash(value):
            if not value:
                return ''
            return hmac.new(
                settings.SECRET_KEY.encode(), value.encode(), hashlib.sha256
            ).hexdigest()

        source_ip_hash = private_hash(client_ip)
        fingerprint = private_hash(f'{email}\n{message.casefold()}')
        recent = ContactUsMessage.objects.filter(date_sent__gte=now - timedelta(days=1))
        if source_ip_hash:
            hourly_count = recent.filter(
                source_ip_hash=source_ip_hash,
                date_sent__gte=now - timedelta(hours=1),
            ).count()
            daily_count = recent.filter(source_ip_hash=source_ip_hash).count()
            if hourly_count >= 5 or daily_count >= 15:
                raise Throttled(detail='Too many contact requests. Please try again later.', wait=3600)
        if recent.filter(email__iexact=email).count() >= 3:
            raise Throttled(detail='Too many contact requests for this email address.', wait=86400)

        reasons = []
        score = 0
        if re.fullmatch(r'[A-Za-z]{12,40}', message) and re.search(r'[A-Z].*[A-Z]', message[1:]):
            score += 6
            reasons.append('random-letter-message')
        if recent.filter(submission_fingerprint=fingerprint).exists():
            score += 6
            reasons.append('duplicate-submission')
        lowered = message.casefold()
        if len(re.findall(r'https?://|www\.', lowered)) >= 2:
            score += 4
            reasons.append('multiple-links')

        serializer.save(
            email=email,
            source_ip_hash=source_ip_hash,
            submission_fingerprint=fingerprint,
            user_agent=self.request.headers.get('X-TAK-User-Agent', '')[:500],
            turnstile_verified=self.request.headers.get('X-TAK-Turnstile-Verified') == '1',
            is_spam=score >= 5,
            spam_score=score,
            spam_reasons=reasons,
        )

class WorkExperienceDetailView(generics.ListAPIView):
    queryset = WorkExperience.objects.all()
    serializer_class = WorkExperienceSerializer
    permission_classes = [LocalOrHasAPIKey]

class ContactInfoView(generics.ListAPIView):
    queryset = ContactInfo.objects.all()
    serializer_class = ContactInfoSeriliazer
    permission_classes = [LocalOrHasAPIKey]

class MobileApplicationListView(generics.ListAPIView):
    serializer_class = MobileApplicationSerializer
    permission_classes = [HasAPIKey]

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return MobileApplication.objects.select_related('project').filter(project__id=project_id)

class DesktopApplicationListView(generics.ListAPIView):
    queryset = DesktopApplication.objects.all()
    serializer_class = DesktopApplicationSerializer
    permission_classes = [HasAPIKey]

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return DesktopApplication.objects.filter(project__id=project_id)

class WebApplicationListView(generics.ListAPIView):
    queryset = WebApplication.objects.all()
    serializer_class = WebApplicationSerializer
    permission_classes = [HasAPIKey]

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return WebApplication.objects.filter(project__id=project_id)
    

def testimonial_form(request, token=None):
    form_submitted = False
    
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form_submitted = True
    else:
        form = TestimonialForm()
    
    return render(request, 'testimonial_form.html', {
        'form': form,
        'form_submitted': form_submitted
    })

def client_feedback_form(request, project_id, token=None):
    project = get_object_or_404(Project, pk=project_id)
    form_submitted = False
    
    # Verify token
    signer = TimestampSigner()
    try:
        value = signer.unsign(token, max_age=60*60*24*7)  # Valid for 7 days
        token_parts = value.split(':')
        if str(project_id) != token_parts[0]:
            return HttpResponse("This feedback link is invalid.", status=400)
    except (BadSignature, SignatureExpired):
        return HttpResponse("This feedback link has expired or is invalid.", status=410)

    invitation = None
    if len(token_parts) == 2:
        invitation = FeedbackInvitation.objects.filter(
            pk=token_parts[1], project=project
        ).first()
        if not invitation or invitation.expires_at < timezone.now():
            return HttpResponse("This feedback link has expired or is invalid.", status=410)
    
    if request.method == 'POST':
        existing_client = ProjectClient.objects.filter(project=project).first()
        form = ProjectClientFeedbackForm(
            request.POST,
            request.FILES,
            instance=existing_client,
        )
        if form.is_valid():
            client = form.save(commit=False)
            client.project = project
            client.is_published = False
            client.submitted_at = timezone.now()
            client.save()
            if invitation:
                invitation.status = FeedbackInvitation.Status.SUBMITTED
                invitation.submitted_at = timezone.now()
                invitation.save(update_fields=("status", "submitted_at"))
            form_submitted = True
    else:
        # Check if client feedback already exists
        try:
            client = ProjectClient.objects.get(project=project)
            form = ProjectClientFeedbackForm(instance=client)
            messages.info(request, "You've already submitted feedback for this project. You can update it below.")
        except ProjectClient.DoesNotExist:
            form = ProjectClientFeedbackForm()
    
    return render(request, 'client_feedback_form.html', {
        'form': form,
        'project': project,
        'form_submitted': form_submitted
    })

def generate_client_feedback_link(project, invitation=None):
    """Generate a secure link for client feedback"""
    signer = TimestampSigner()
    value = str(project.id)
    if invitation is not None:
        value = f"{project.id}:{invitation.id}"
    token = signer.sign(value)
    return token

def send_feedback_request_email(project, recipient_email, recipient_name):
    """Send an email with the client feedback link"""
    invitation = FeedbackInvitation.objects.create(
        project=project,
        recipient_email=recipient_email,
        recipient_name=recipient_name,
        expires_at=timezone.now() + timedelta(days=7),
    )
    token = generate_client_feedback_link(project, invitation)
    feedback_url = reverse('client_feedback_form', kwargs={'project_id': project.id, 'token': token})
    absolute_url = settings.BACKEND_PUBLIC_URL + feedback_url
    
    subject = f"We'd like your feedback on {project.title}"
    html_message = render_to_string('email/feedback_request_email.html', {
        'project': project,
        'recipient_name': recipient_name,
        'feedback_url': absolute_url
    })
    
    if settings.DEBUG and not settings.RESEND_API_KEY:
        invitation.status = FeedbackInvitation.Status.DELIVERED
        invitation.delivery_mode = "local-preview"
        invitation.sent_at = timezone.now()
        invitation.save(update_fields=("status", "delivery_mode", "sent_at"))
        return True
    if not settings.RESEND_API_KEY:
        invitation.status = FeedbackInvitation.Status.FAILED
        invitation.last_error = "RESEND_API_KEY is not configured."
        invitation.save(update_fields=("status", "last_error"))
        return False
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": settings.RESEND_FROM_EMAIL,
                "to": [recipient_email],
                "subject": subject,
                "text": f"Please share your feedback about {project.title} at: {absolute_url}",
                "html": html_message,
                "reply_to": "info@takkinship.com",
            },
            timeout=settings.EMAIL_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        invitation.status = FeedbackInvitation.Status.FAILED
        invitation.last_error = str(exc)[:1000]
        invitation.save(update_fields=("status", "last_error"))
        return False
    invitation.status = FeedbackInvitation.Status.DELIVERED
    invitation.provider_message_id = response.json().get("id", "")
    invitation.delivery_mode = "resend"
    invitation.sent_at = timezone.now()
    invitation.save(update_fields=("status", "provider_message_id", "delivery_mode", "sent_at"))
    return True
