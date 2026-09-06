from django.contrib import admin

from .models import AuditEvent, ManagedProject, ProjectMembership


@admin.register(ManagedProject)
class ManagedProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "project_type", "status", "module_key", "updated_at")
    list_filter = ("project_type", "status")
    search_fields = ("name", "slug", "module_key")


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "role", "is_active", "updated_at")
    list_filter = ("role", "is_active")
    search_fields = ("project__name", "user__username", "user__email")


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("action", "project", "actor", "created_at")
    list_filter = ("project",)
    search_fields = ("action", "target_type", "target_id")
    readonly_fields = ("project", "actor", "action", "target_type", "target_id", "metadata", "created_at")
