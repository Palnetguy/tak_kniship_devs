from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import AuditEvent, ManagedProject, ProjectMembership


class AdminUserSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "first_name", "last_name", "display_name", "is_superuser")

    def get_display_name(self, user):
        return user.get_full_name() or user.username


class ManagedProjectSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ManagedProject
        fields = (
            "id", "slug", "name", "project_type", "status", "description", "public_url",
            "repository_url", "module_key", "member_count", "created_at", "updated_at",
        )
        read_only_fields = ("id", "slug", "member_count", "created_at", "updated_at")


class ProjectMembershipSerializer(serializers.ModelSerializer):
    user = AdminUserSerializer(read_only=True)

    class Meta:
        model = ProjectMembership
        fields = ("id", "project", "user", "role", "is_active", "created_at", "updated_at")


class AuditEventSerializer(serializers.ModelSerializer):
    actor = AdminUserSerializer(read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = AuditEvent
        fields = (
            "id", "project", "project_name", "actor", "action", "target_type", "target_id",
            "metadata", "created_at",
        )
