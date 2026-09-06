from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import AuditEvent, ManagedProject, ProjectMembership
from tak_devs_app.models import ContactInfo, ContactUsMessage, FAQ, Gallery, Project, TeamMember, Testimonial


class AdminUserSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "first_name", "last_name", "display_name", "is_active", "is_staff", "is_superuser")

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


class PortfolioProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "id", "title", "project_category", "quote", "about_project", "challenges_faced",
            "date_published", "duration_of_development", "tech_stack",
        )


class TeamMemberAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ("id", "profile_picture", "name", "role", "biography", "instagram", "linkedin", "twitter", "order")


class TestimonialAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ("id", "user_photo", "name", "comment", "job_title")


class FAQAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ("id", "title", "description")


class GalleryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ("id", "image")


class ContactInfoAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = "__all__"


class ContactMessageAdminSerializer(serializers.ModelSerializer):
    handled_by_name = serializers.CharField(source="handled_by.get_full_name", read_only=True)

    class Meta:
        model = ContactUsMessage
        fields = (
            "id", "name", "subject", "email", "message", "phone_number", "date_sent",
            "handled_at", "handled_by", "handled_by_name",
        )
        read_only_fields = ("date_sent", "handled_by", "handled_by_name")
