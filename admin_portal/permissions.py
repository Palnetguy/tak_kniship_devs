from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import ProjectMembership


class IsTAKAdmin(BasePermission):
    message = "A TAK staff account is required to use the administration platform."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


class IsPlatformOwner(IsTAKAdmin):
    message = "A platform owner is required to manage admin accounts."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class HasTAKWebsiteAccess(IsTAKAdmin):
    """Restrict the website module to active project members."""

    message = "Access to the TAK Kinship website project is required."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.user.is_superuser:
            return True

        roles = ProjectMembership.objects.filter(
            project__slug="tak-kinship",
            user=request.user,
            is_active=True,
        ).values_list("role", flat=True)
        if request.method in SAFE_METHODS:
            return roles.exists()
        return roles.filter(
            role__in=(
                ProjectMembership.Role.OWNER,
                ProjectMembership.Role.ADMIN,
                ProjectMembership.Role.EDITOR,
            )
        ).exists()
