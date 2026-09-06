from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuditEvent, ManagedProject
from .permissions import IsTAKAdmin
from .serializers import AdminUserSerializer, AuditEventSerializer, ManagedProjectSerializer


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
                    "team_memberships": sum(project.memberships.filter(is_active=True).count() for project in projects),
                    "recent_activity": AuditEvent.objects.count(),
                },
                "projects": ManagedProjectSerializer(
                    projects.annotate(member_count=Count("memberships", distinct=True))[:6], many=True
                ).data,
                "activity": AuditEventSerializer(recent_events, many=True).data,
            }
        )


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
