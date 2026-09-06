from rest_framework.permissions import BasePermission


class IsTAKAdmin(BasePermission):
    message = "A TAK staff account is required to use the administration platform."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))
