from django.contrib.auth import get_user_model
from django.utils.text import slugify
from rest_framework import serializers

from .models import AuditEvent, ManagedProject, ProjectMembership, WebsiteContent


class WebsiteContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteContent
        fields = ("id", "project", "key", "value", "is_published", "created_at", "updated_at")
        read_only_fields = ("id", "project", "created_at", "updated_at")
from tak_devs_app.models import (
    ContactInfo, ContactUsMessage, DesktopApplication, FAQ, Gallery, MobileApplication,
    Project, ProjectClient, ProjectFeature, ProjectImage, TeamMember, TechStack, Testimonial,
    WebApplication,
)


class AdminUserSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    project_access = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "first_name", "last_name", "display_name", "is_active", "is_staff", "is_superuser", "project_access")

    def get_display_name(self, user):
        return user.get_full_name() or user.username

    def get_project_access(self, user):
        return [{"project": membership.project.slug, "role": membership.role}
                for membership in user.project_memberships.select_related("project").filter(is_active=True)]


class AdminAccountWriteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=12)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "first_name", "last_name", "password", "is_active")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = get_user_model().objects.create_user(password=password, is_staff=True, **validated_data)
        project = ManagedProject.objects.filter(slug="tak-kinship").first()
        if project:
            ProjectMembership.objects.get_or_create(
                project=project,
                user=user,
                defaults={"role": ProjectMembership.Role.ADMIN},
            )
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


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
    tech_stack_names = serializers.ListField(child=serializers.CharField(max_length=120), write_only=True, required=False)
    tech_stack_labels = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            "id", "title", "slug", "project_category", "quote", "overview", "problem", "solution", "status", "about_project", "challenges_faced",
            "date_published", "duration_of_development", "is_published", "tech_stack", "tech_stack_names", "tech_stack_labels",
        )

    def get_tech_stack_labels(self, project):
        return list(project.tech_stack.values_list("language", flat=True))

    def _set_tech_stack(self, project, names):
        if names is None:
            return
        stacks = [TechStack.objects.get_or_create(language=name.strip())[0] for name in names if name.strip()]
        project.tech_stack.set(stacks)

    def create(self, validated_data):
        names = validated_data.pop("tech_stack_names", None)
        if not validated_data.get("slug"):
            validated_data["slug"] = self._available_slug(validated_data["title"])
        project = super().create(validated_data)
        self._set_tech_stack(project, names)
        return project

    def update(self, instance, validated_data):
        names = validated_data.pop("tech_stack_names", None)
        project = super().update(instance, validated_data)
        self._set_tech_stack(project, names)
        return project

    def _available_slug(self, title):
        base = slugify(title) or "project"
        candidate = base
        suffix = 2
        while Project.objects.filter(slug=candidate).exists():
            candidate = f"{base}-{suffix}"
            suffix += 1
        return candidate


class ProjectImageAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = ("id", "project", "image", "image_type", "caption", "order")


class ProjectFeatureAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFeature
        fields = ("id", "project", "title", "description")


class ProjectClientAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectClient
        fields = ("id", "project", "name", "location", "rating", "message", "profile_image")


class MobileApplicationAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileApplication
        fields = ("id", "project", "name", "version", "icon", "apk", "apk_url", "download_id", "description", "date_released")
        read_only_fields = ("date_released",)


class DesktopApplicationAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesktopApplication
        fields = ("id", "project", "name", "version", "icon", "apk", "apk_url", "download_id", "description", "date_released")
        read_only_fields = ("date_released",)


class WebApplicationAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebApplication
        fields = ("id", "project", "name", "icon", "url")


class TeamMemberAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ("id", "profile_picture", "name", "role", "biography", "instagram", "linkedin", "twitter", "order", "is_published")


class TestimonialAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ("id", "user_photo", "name", "comment", "job_title", "is_published")


class FAQAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ("id", "title", "description", "is_published")


class GalleryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ("id", "image", "is_published")


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
