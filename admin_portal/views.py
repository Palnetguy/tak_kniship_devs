from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db.models import Count
from django.utils import timezone
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from .models import AuditEvent, ManagedProject
from .permissions import IsTAKAdmin
from .serializers import (
    AdminUserSerializer, AuditEventSerializer, ContactInfoAdminSerializer,
    ContactMessageAdminSerializer, FAQAdminSerializer, GalleryAdminSerializer,
    ManagedProjectSerializer, PortfolioProjectSerializer, TeamMemberAdminSerializer,
    TestimonialAdminSerializer,
)
from tak_devs_app.models import ContactInfo, ContactUsMessage, FAQ, Gallery, Project, TeamMember, Testimonial


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


class LogoutView(APIView):
    permission_classes = (IsTAKAdmin,)

    def post(self, request):
        record_event(actor=request.user, action="admin.auth.signed_out")
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(APIView):
    permission_classes = (IsTAKAdmin,)

    def get(self, request):
        return Response({"user": AdminUserSerializer(request.user).data})


class DashboardView(APIView):
    permission_classes = (IsTAKAdmin,)

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

    permission_classes = (IsTAKAdmin,)

    def get(self, request):
        project = ManagedProject.objects.filter(slug="tak-kinship").first()
        activity = AuditEvent.objects.select_related("project", "actor")
        if project:
            activity = activity.filter(project=project)

        return Response(
            {
                "summary": {
                    "open_enquiries": ContactUsMessage.objects.filter(handled_at__isnull=True).count(),
                    "portfolio_projects": Project.objects.count(),
                    "team_members": TeamMember.objects.count(),
                    "content_items": FAQ.objects.count(),
                },
                "activity": AuditEventSerializer(activity[:8], many=True).data,
            }
        )


class AdminAccountListView(APIView):
    permission_classes = (IsTAKAdmin,)

    def get(self, request):
        accounts = get_user_model().objects.filter(is_staff=True).order_by("username")
        return Response({"accounts": AdminUserSerializer(accounts, many=True).data})


class ProjectListView(APIView):
    permission_classes = (IsTAKAdmin,)

    def get(self, request):
        projects = ManagedProject.objects.annotate(member_count=Count("memberships", distinct=True))
        return Response({"projects": ManagedProjectSerializer(projects, many=True).data})


class ProjectDetailView(APIView):
    permission_classes = (IsTAKAdmin,)

    def get_object(self, slug):
        return ManagedProject.objects.annotate(member_count=Count("memberships", distinct=True)).get(slug=slug)

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


class PortfolioProjectViewSet(AuditedModelViewSet):
    queryset = Project.objects.prefetch_related("tech_stack").order_by("-date_published", "-id")
    serializer_class = PortfolioProjectSerializer
    audit_namespace = "admin.portfolio"


class TeamMemberViewSet(AuditedModelViewSet):
    queryset = TeamMember.objects.all().order_by("order", "name")
    serializer_class = TeamMemberAdminSerializer
    audit_namespace = "admin.team"


class TestimonialViewSet(AuditedModelViewSet):
    queryset = Testimonial.objects.all().order_by("name")
    serializer_class = TestimonialAdminSerializer
    audit_namespace = "admin.testimonials"


class FAQViewSet(AuditedModelViewSet):
    queryset = FAQ.objects.all().order_by("id")
    serializer_class = FAQAdminSerializer
    audit_namespace = "admin.faqs"


class GalleryViewSet(AuditedModelViewSet):
    queryset = Gallery.objects.all().order_by("id")
    serializer_class = GalleryAdminSerializer
    audit_namespace = "admin.media"


class ContactInfoViewSet(AuditedModelViewSet):
    queryset = ContactInfo.objects.all().order_by("id")
    serializer_class = ContactInfoAdminSerializer
    audit_namespace = "admin.contact_info"


class ContactMessageViewSet(AuditedModelViewSet):
    queryset = ContactUsMessage.objects.select_related("handled_by").order_by("-date_sent")
    serializer_class = ContactMessageAdminSerializer
    audit_namespace = "admin.messages"
    http_method_names = ("get", "patch", "head", "options")

    def perform_update(self, serializer):
        instance = serializer.save(
            handled_by=self.request.user if serializer.validated_data.get("handled_at") else None,
            handled_at=serializer.validated_data.get("handled_at") or None,
        )
        self._record("updated", instance)
