from django.conf import settings
from django.db import models


class ManagedProject(models.Model):
    """A coded-in project registered with the shared TAK administration platform."""

    class ProjectType(models.TextChoices):
        WEBSITE = "website", "Website"
        MOBILE_APP = "mobile_app", "Mobile application"
        DESKTOP_APP = "desktop_app", "Desktop application"
        API = "api", "API"
        SERVICE = "service", "Service"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        ARCHIVED = "archived", "Archived"

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=160)
    project_type = models.CharField(max_length=32, choices=ProjectType.choices)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    description = models.TextField(blank=True)
    public_url = models.URLField(blank=True)
    repository_url = models.URLField(blank=True)
    module_key = models.SlugField(
        help_text="The application module implemented for this project by the development team."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProjectMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Administrator"
        EDITOR = "editor", "Editor"
        VIEWER = "viewer", "Viewer"

    project = models.ForeignKey(
        ManagedProject, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project_memberships"
    )
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.VIEWER)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["project", "user"], name="unique_project_membership")
        ]

    def __str__(self):
        return f"{self.user} on {self.project} ({self.role})"


class AuditEvent(models.Model):
    project = models.ForeignKey(
        ManagedProject,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_events",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="admin_audit_events",
    )
    action = models.CharField(max_length=120)
    target_type = models.CharField(max_length=80, blank=True)
    target_id = models.CharField(max_length=80, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["project", "-created_at"])]

    def __str__(self):
        return self.action
