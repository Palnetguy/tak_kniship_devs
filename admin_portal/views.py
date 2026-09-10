import requests
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.template.loader import render_to_string
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.throttling import ScopedRateThrottle

from .models import AuditEvent, ContactMessageReply, ManagedProject, WebsiteContent
from .permissions import HasTAKWebsiteAccess, IsPlatformOwner, IsTAKAdmin
from .serializers import (
    AdminAccountWriteSerializer, AdminUserSerializer, AuditEventSerializer, ContactInfoAdminSerializer,
    ContactMessageAdminSerializer, FAQAdminSerializer, GalleryAdminSerializer,
    ManagedProjectSerializer, PortfolioProjectSerializer, TeamMemberAdminSerializer,
    TestimonialAdminSerializer, ProjectImageAdminSerializer, ProjectFeatureAdminSerializer,
    ProjectClientAdminSerializer, FeedbackInvitationAdminSerializer, MobileApplicationAdminSerializer, DesktopApplicationAdminSerializer,
    AgreementAdminSerializer, WebApplicationAdminSerializer, WorkExperienceAdminSerializer,
    WebsiteContentSerializer,
)
from tak_devs_app.models import (
    Agreement, ContactInfo, ContactUsMessage, DesktopApplication, FAQ, FeedbackInvitation, Gallery, MobileApplication, Project,
    ProjectClient, ProjectFeature, ProjectImage, TeamMember, Testimonial, WebApplication, WorkExperience,
)
from tak_devs_app.views import generate_client_feedback_link


def deliver_outbound_email(*, recipient, subject, body, html):
    """Send through Resend in production and safely preview in local development."""
    if settings.DEBUG and not settings.RESEND_API_KEY:
        return {"id": "local-preview", "mode": "local-preview"}
    if not settings.RESEND_API_KEY:
        raise ValidationError({"detail": "RESEND_API_KEY is not configured."})
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": settings.RESEND_FROM_EMAIL,
                "to": [recipient],
                "subject": subject,
                "text": body,
                "html": html,
                "reply_to": "info@takkinship.com",
            },
            timeout=settings.EMAIL_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ValidationError({"detail": "The email provider could not deliver this message."}) from exc
    return {"id": response.json().get("id", ""), "mode": "resend"}


def record_event(*, actor, action, project=None, target_type="", target_id="", metadata=None):
    return AuditEvent.objects.create(
        actor=actor,
        project=project,
        action=action,
        target_type=target_type,
        target_id=str(target_id),
        metadata=metadata or {},
    )


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request):
        return Response({"csrfToken": get_token(request)})


@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "admin_login"

    def post(self, request):
        username = str(request.data.get("username", "")).strip()
        password = request.data.get("password", "")
        if not username or not password:
            return Response(
                {"detail": "Enter both your username and password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)
        if user is None or not (user.is_staff or user.is_superuser):
            return Response(
                {"detail": "These credentials do not have administration access."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)
        record_event(actor=user, action="admin.auth.signed_in")
        return Response({"user": AdminUserSerializer(user).data})


@method_decorator(csrf_protect, name="dispatch")
class LogoutView(APIView):
    """Clear the browser session even when it has expired or lost access."""

    permission_classes = (AllowAny,)

    def post(self, request):
        if request.user.is_authenticated:
            record_event(actor=request.user, action="admin.auth.signed_out")
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(APIView):
    permission_classes = (IsTAKAdmin,)

    def get(self, request):
        return Response({"user": AdminUserSerializer(request.user).data})


class DashboardView(APIView):
    permission_classes = (IsPlatformOwner,)

    def get(self, request):
        projects = ManagedProject.objects.all()
        recent_events = AuditEvent.objects.select_related("project", "actor")[:8]
        return Response(
            {
                "summary": {
                    "projects": projects.count(),
                    "active_projects": projects.filter(status=ManagedProject.Status.ACTIVE).count(),
                    "admin_accounts": get_user_model().objects.filter(is_staff=True, is_active=True).count(),
                    "recent_activity": AuditEvent.objects.count(),
                },
                "projects": ManagedProjectSerializer(
                    projects.annotate(member_count=Count("memberships", distinct=True))[:6], many=True
                ).data,
                "activity": AuditEventSerializer(recent_events, many=True).data,
            }
        )


class WebsiteOverviewView(APIView):
    """TAK Kinship's current Website module. Other project types add their own modules."""

    permission_classes = (HasTAKWebsiteAccess,)

    def get(self, request):
        project = ManagedProject.objects.filter(slug="tak-kinship").first()
        activity = AuditEvent.objects.select_related("project", "actor")
        if project:
            activity = activity.filter(project=project)

        return Response(
            {
                "summary": {
                    "open_enquiries": ContactUsMessage.objects.filter(
                        handled_at__isnull=True, is_spam=False
                    ).count(),
                    "portfolio_projects": Project.objects.count(),
                    "team_members": TeamMember.objects.count(),
                    "content_items": FAQ.objects.count(),
                    "media_items": Gallery.objects.count(),
                    "testimonials": Testimonial.objects.count(),
                },
                "activity": AuditEventSerializer(activity[:8], many=True).data,
            }
        )


class DeploymentSettingsView(APIView):
    """Report operational readiness without exposing secret values."""

    permission_classes = (IsPlatformOwner,)

    def get(self, request):
        return Response({
            "environment": "development" if settings.DEBUG else "production",
            "public_site_url": settings.PUBLIC_SITE_URL,
            "admin_site_url": settings.ADMIN_SITE_URL,
            "backend_public_url": settings.BACKEND_PUBLIC_URL,
            "checks": {
                "database": "sqlite" if settings.USE_SQLITE else "postgresql",
                "resend_configured": bool(settings.RESEND_API_KEY),
                "admin_recipients_configured": bool(settings.ADMIN_EMAILS),
                "media_storage": "local" if settings.USE_SQLITE else "s3",
            },
        })


class PublicWebsiteContentView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request, key):
        content = WebsiteContent.objects.filter(project__slug="tak-kinship", key=key, is_published=True).first()
        if not content:
            return Response({"detail": "Published content was not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(WebsiteContentSerializer(content).data)


class AdminAccountListView(APIView):
    permission_classes = (IsPlatformOwner,)

    def get(self, request):
        accounts = get_user_model().objects.filter(is_staff=True).order_by("username")
        return Response({"accounts": AdminUserSerializer(accounts, many=True).data})

    def post(self, request):
        serializer = AdminAccountWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = serializer.save()
        record_event(actor=request.user, action="admin.accounts.created", target_type="auth.user", target_id=account.pk)
        return Response({"account": AdminUserSerializer(account).data}, status=status.HTTP_201_CREATED)


class AdminAccountDetailView(APIView):
    permission_classes = (IsPlatformOwner,)

    def get_object(self, pk):
        return get_object_or_404(get_user_model(), pk=pk, is_staff=True)

    def patch(self, request, pk):
        account = self.get_object(pk)
        if account == request.user and request.data.get("is_active") is False:
            return Response({"detail": "You cannot deactivate your own account."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = AdminAccountWriteSerializer(account, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        account = serializer.save()
        record_event(actor=request.user, action="admin.accounts.updated", target_type="auth.user", target_id=account.pk)
        return Response({"account": AdminUserSerializer(account).data})


class ActivityListView(APIView):
    permission_classes = (IsPlatformOwner,)

    def get(self, request):
        events = AuditEvent.objects.select_related("project", "actor")
        if not request.user.is_superuser:
            events = events.filter(
                Q(project__memberships__user=request.user, project__memberships__is_active=True)
                | Q(project__isnull=True)
            ).distinct()
        project = request.query_params.get("project")
        action = request.query_params.get("action")
        if project:
            events = events.filter(project__slug=project)
        if action:
            events = events.filter(action__icontains=action)
        return Response({"activity": AuditEventSerializer(events[:100], many=True).data})


class ProjectListView(APIView):
    permission_classes = (IsPlatformOwner,)

    def get(self, request):
        projects = ManagedProject.objects.annotate(member_count=Count("memberships", distinct=True))
        if not request.user.is_superuser:
            projects = projects.filter(memberships__user=request.user, memberships__is_active=True)
        return Response({"projects": ManagedProjectSerializer(projects, many=True).data})


class ProjectDetailView(APIView):
    permission_classes = (IsPlatformOwner,)

    def get_object(self, slug):
        projects = ManagedProject.objects.annotate(member_count=Count("memberships", distinct=True))
        if not self.request.user.is_superuser:
            projects = projects.filter(
                memberships__user=self.request.user,
                memberships__is_active=True,
            )
        return get_object_or_404(projects, slug=slug)

    def get(self, request, slug):
        project = self.get_object(slug)
        return Response({"project": ManagedProjectSerializer(project).data})


class AuditedModelViewSet(viewsets.ModelViewSet):
    permission_classes = (IsTAKAdmin,)
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    audit_namespace = "admin.content"

    def _record(self, action, instance):
        website_project = ManagedProject.objects.filter(slug="tak-kinship").first()
        record_event(
            actor=self.request.user,
            project=website_project,
            action=f"{self.audit_namespace}.{action}",
            target_type=instance._meta.label_lower,
            target_id=instance.pk,
        )

    def perform_create(self, serializer):
        instance = serializer.save()
        self._record("created", instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        self._record("updated", instance)

    def perform_destroy(self, instance):
        self._record("deleted", instance)
        instance.delete()


class WebsiteContentViewSet(AuditedModelViewSet):
    permission_classes = (HasTAKWebsiteAccess,)
    serializer_class = WebsiteContentSerializer
    audit_namespace = "admin.website_content"

    def get_queryset(self):
        return WebsiteContent.objects.filter(project__slug="tak-kinship")

    def perform_create(self, serializer):
        project = ManagedProject.objects.get(slug="tak-kinship")
        instance = serializer.save(project=project)
        self._record("created", instance)


class PortfolioProjectViewSet(AuditedModelViewSet):
    permission_classes = (HasTAKWebsiteAccess,)
    queryset = Project.objects.prefetch_related("tech_stack").order_by("-date_published", "-id")
    serializer_class = PortfolioProjectSerializer
    audit_namespace = "admin.portfolio"


class ProjectImageViewSet(AuditedModelViewSet):
    permission_classes = (HasTAKWebsiteAccess,)
    queryset = ProjectImage.objects.select_related("project").order_by("project_id", "image_type", "order", "id")
    serializer_class = ProjectImageAdminSerializer
    audit_namespace = "admin.project_images"


class ProjectFeatureViewSet(AuditedModelViewSet):
    permission_classes = (HasTAKWebsiteAccess,)
    queryset = ProjectFeature.objects.select_related("project").order_by("project_id", "id")
    serializer_class = ProjectFeatureAdminSerializer
    audit_namespace = "admin.project_features"


class ProjectClientViewSet(AuditedModelViewSet):
    permission_classes = (HasTAKWebsiteAccess,)
    queryset = ProjectClient.objects.select_related("project").order_by("project_id")
    serializer_class = ProjectClientAdminSerializer
    audit_namespace = "admin.project_clients"


class FeedbackInvitationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (HasTAKWebsiteAccess,)
    queryset = FeedbackInvitation.objects.select_related("project", "created_by")
    serializer_class = FeedbackInvitationAdminSerializer

    @action(detail=True, methods=("post",))
    def resend(self, request, pk=None):
        invitation = self.get_object()
        return _deliver_feedback_invitation(request, invitation.project, invitation)


class MobileApplicationViewSet(AuditedModelViewSet):
    permission_classes = (HasTAKWebsiteAccess,)
    queryset = MobileApplication.objects.select_related("project").order_by("project_id", "name")
    serializer_class = MobileApplicationAdminSerializer
    audit_namespace = "admin.mobile_applications"


class DesktopApplicationViewSet(AuditedModelViewSet):
    permission_classes = (HasTAKWebsiteAccess,)
    queryset = DesktopApplication.objects.select_related("project").order_by("project_id", "name")
    serializer_class = DesktopApplicationAdminSerializer
    audit_namespace = "admin.desktop_applications"


class WebApplicationViewSet(AuditedModelViewSet):
    permission_classes = (HasTAKWebsiteAccess,)
    queryset = WebApplication.objects.select_related("project").order_by("project_id", "name")
    serializer_class = WebApplicationAdminSerializer
    audit_namespace = "admin.web_applications"


class AgreementViewSet(AuditedModelViewSet):
    permission_classes = (HasTAKWebsiteAccess,)
    queryset = Agreement.objects.select_related("project").order_by("project_id", "agreement_type")
    serializer_class = AgreementAdminSerializer
    audit_namespace = "admin.agreements"


class WorkExperienceViewSet(AuditedModelViewSet):
    permission_classes = (HasTAKWebsiteAccess,)
    queryset = WorkExperience.objects.all().order_by("id")
    serializer_class = WorkExperienceAdminSerializer
    audit_namespace = "admin.work_experience"


class TeamMemberViewSet(AuditedModelViewSet):
    permission_classes = (HasTAKWebsiteAccess,)
    queryset = TeamMember.objects.all().order_by("order", "name")
    serializer_class = TeamMemberAdminSerializer
    audit_namespace = "admin.team"

    @action(detail=False, methods=["post"])
    def reorder(self, request):
        ordered_ids = request.data.get("ordered_ids")
        if not isinstance(ordered_ids, list) or not ordered_ids:
            raise ValidationError({"ordered_ids": "Provide the team member IDs in display order."})
        try:
            ordered_ids = [int(member_id) for member_id in ordered_ids]
        except (TypeError, ValueError) as exc:
            raise ValidationError({"ordered_ids": "Every team member ID must be a number."}) from exc
        if len(ordered_ids) != len(set(ordered_ids)):
            raise ValidationError({"ordered_ids": "Team member IDs cannot be repeated."})

        members = list(TeamMember.objects.filter(pk__in=ordered_ids))
        if len(members) != len(ordered_ids):
            raise ValidationError({"ordered_ids": "One or more team members were not found."})
        by_id = {member.pk: member for member in members}
        with transaction.atomic():
            for position, member_id in enumerate(ordered_ids, start=1):
                by_id[member_id].order = position
            TeamMember.objects.bulk_update(members, ["order"])
            self._record("reordered", by_id[ordered_ids[0]])

        ordered_members = [by_id[member_id] for member_id in ordered_ids]
        return Response(TeamMemberAdminSerializer(ordered_members, many=True, context={"request": request}).data)


class TestimonialViewSet(AuditedModelViewSet):
    permission_classes = (HasTAKWebsiteAccess,)
    queryset = Testimonial.objects.all().order_by("name")
    serializer_class = TestimonialAdminSerializer
    audit_namespace = "admin.testimonials"


class FAQViewSet(AuditedModelViewSet):
    permission_classes = (HasTAKWebsiteAccess,)
    queryset = FAQ.objects.all().order_by("id")
    serializer_class = FAQAdminSerializer
    audit_namespace = "admin.faqs"


class GalleryViewSet(AuditedModelViewSet):
    permission_classes = (HasTAKWebsiteAccess,)
    queryset = Gallery.objects.all().order_by("id")
    serializer_class = GalleryAdminSerializer
    audit_namespace = "admin.media"


class ContactInfoViewSet(AuditedModelViewSet):
    permission_classes = (HasTAKWebsiteAccess,)
    queryset = ContactInfo.objects.all().order_by("id")
    serializer_class = ContactInfoAdminSerializer
    audit_namespace = "admin.contact_info"

    def perform_create(self, serializer):
        if ContactInfo.objects.exists():
            raise ValidationError(
                {"detail": "Contact information already exists; update the existing record."}
            )
        super().perform_create(serializer)


class ContactMessageViewSet(AuditedModelViewSet):
    permission_classes = (HasTAKWebsiteAccess,)
    queryset = ContactUsMessage.objects.select_related("handled_by").prefetch_related(
        "replies__sent_by"
    ).order_by("-date_sent")
    serializer_class = ContactMessageAdminSerializer
    audit_namespace = "admin.messages"
    http_method_names = ("get", "patch", "post", "head", "options")

    @action(detail=True, methods=("post",))
    def reply(self, request, pk=None):
        message = self.get_object()
        subject = str(request.data.get("subject", "")).strip()
        body = str(request.data.get("body", "")).strip()
        if not subject or not body:
            raise ValidationError({"detail": "Enter both a reply subject and message."})
        if len(subject) > 255 or len(body) > 10000:
            raise ValidationError({"detail": "The reply is longer than the allowed limit."})
        delivery = deliver_outbound_email(
            recipient=message.email,
            subject=subject,
            body=body,
            html=(
                '<div style="font-family:Arial,sans-serif;line-height:1.65;color:#152019">'
                f'<p>{escape(body).replace(chr(10), "<br>")}</p>'
                '<p style="margin-top:32px;color:#4a5b51">TAK Kinship Technologies Limited</p>'
                '</div>'
            ),
        )
        ContactMessageReply.objects.create(
            contact_message=message,
            sent_by=request.user,
            subject=subject,
            body=body,
            provider_message_id=delivery["id"],
            delivery_mode=delivery["mode"],
        )
        message.handled_at = timezone.now()
        message.handled_by = request.user
        message.save(update_fields=("handled_at", "handled_by"))
        self._record("replied", message)
        return Response(ContactMessageAdminSerializer(message).data)

    def perform_update(self, serializer):
        if "handled_at" in serializer.validated_data:
            handled_at = serializer.validated_data.get("handled_at")
            instance = serializer.save(
                handled_by=self.request.user if handled_at else None,
                handled_at=handled_at,
            )
        else:
            instance = serializer.save()
        self._record("updated", instance)


class ProjectFeedbackRequestView(APIView):
    permission_classes = (HasTAKWebsiteAccess,)

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        recipient_email = str(request.data.get("recipient_email", "")).strip()
        recipient_name = str(request.data.get("recipient_name", "")).strip()
        if not recipient_email or not recipient_name:
            raise ValidationError({"detail": "Enter the client's name and email address."})
        try:
            validate_email(recipient_email)
        except DjangoValidationError as exc:
            raise ValidationError({"recipient_email": "Enter a valid email address."}) from exc
        invitation = FeedbackInvitation.objects.create(
            project=project,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            expires_at=timezone.now() + timedelta(days=7),
            created_by=request.user,
        )
        return _deliver_feedback_invitation(request, project, invitation)


def _deliver_feedback_invitation(request, project, invitation):
    invitation.expires_at = timezone.now() + timedelta(days=7)
    invitation.status = FeedbackInvitation.Status.PENDING
    invitation.last_error = ""
    invitation.save(update_fields=("expires_at", "status", "last_error"))
    token = generate_client_feedback_link(project, invitation)
    feedback_path = reverse("client_feedback_form", kwargs={"project_id": project.pk, "token": token})
    feedback_url = request.build_absolute_uri(feedback_path)
    subject = f"We'd like your feedback on {project.title}"
    body = f"Hello {invitation.recipient_name},\n\nPlease share your feedback about {project.title}: {feedback_url}"
    try:
        delivery = deliver_outbound_email(
            recipient=invitation.recipient_email,
            subject=subject,
            body=body,
            html=render_to_string(
                "email/feedback_request_email.html",
                {"project": project, "recipient_name": invitation.recipient_name, "feedback_url": feedback_url},
            ),
        )
    except ValidationError as exc:
        invitation.status = FeedbackInvitation.Status.FAILED
        invitation.last_error = str(exc.detail)
        invitation.save(update_fields=("status", "last_error"))
        raise
    invitation.status = FeedbackInvitation.Status.DELIVERED
    invitation.delivery_mode = delivery["mode"]
    invitation.provider_message_id = delivery["id"]
    invitation.sent_at = timezone.now()
    invitation.save(update_fields=("status", "delivery_mode", "provider_message_id", "sent_at"))
    website_project = ManagedProject.objects.filter(slug="tak-kinship").first()
    record_event(
        actor=request.user,
        project=website_project,
        action="admin.portfolio.feedback_requested",
        target_type=project._meta.label_lower,
        target_id=project.pk,
        metadata={"recipient": invitation.recipient_email, "delivery_mode": delivery["mode"], "invitation_id": invitation.pk},
    )
    return Response({
        "detail": "Feedback request sent.",
        "delivery_mode": delivery["mode"],
        "invitation": FeedbackInvitationAdminSerializer(invitation).data,
    })
