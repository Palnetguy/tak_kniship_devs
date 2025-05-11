from django.contrib import admin
from django.utils.html import format_html
from .models import (
    FAQ, Agreement, ContactInfo, ContactUsMessage, DesktopApplication,
    Gallery, MobileApplication, Project, TeamMember, TechStack,
    Testimonial, WebApplication, WorkExperience, ProjectFeature, ProjectClient, ProjectImage
)

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ('image', 'image_type', 'caption', 'order')
    min_num = 0
    max_num = 10

class ProjectFeatureInline(admin.TabularInline):
    model = ProjectFeature
    extra = 1

class ProjectClientInline(admin.StackedInline):
    model = ProjectClient

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_category', 'date_published')
    list_filter = ('project_category', 'date_published')
    search_fields = ('title', 'about_project')
    filter_horizontal = ('tech_stack',)
    inlines = [ProjectImageInline, ProjectFeatureInline, ProjectClientInline]

@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ('project', 'image_type', 'display_image', 'order')
    list_filter = ('image_type', 'project')
    search_fields = ('project__title', 'caption')
    ordering = ('order',)

    def display_image(self, obj):
        if (obj.image):
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return ""
    display_image.short_description = 'Preview'

@admin.register(ProjectFeature)
class ProjectFeatureAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'description_preview')
    list_filter = ('project',)
    search_fields = ('title', 'description', 'project__title')

    def description_preview(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    description_preview.short_description = 'Description Preview'

@admin.register(ProjectClient)
class ProjectClientAdmin(admin.ModelAdmin):
    list_display = ('project', 'name', 'location', 'rating', 'message_preview')
    list_filter = ('rating', 'location')
    search_fields = ('name', 'location', 'message', 'project__title')

    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Message Preview'

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'display_profile_picture', 'social_links')
    list_filter = ('role',)
    search_fields = ('name', 'role', 'biography')

    def display_profile_picture(self, obj):
        return format_html('<img src="{}" width="50" height="50" />', obj.profile_picture.url)
    display_profile_picture.short_description = 'Profile Picture'

    def social_links(self, obj):
        links = []
        if obj.linkedin:
            links.append(f'<a href="{obj.linkedin}" target="_blank">LinkedIn</a>')
        if obj.twitter:
            links.append(f'<a href="{obj.twitter}" target="_blank">Twitter</a>')
        if obj.instagram:
            links.append(f'<a href="{obj.instagram}" target="_blank">Instagram</a>')
        return format_html(' | '.join(links))
    social_links.short_description = 'Social Media'

@admin.register(ContactUsMessage)
class ContactUsMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'phone_number', 'date_sent')
    list_filter = ('date_sent',)
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('date_sent',)
    date_hierarchy = 'date_sent'

@admin.register(MobileApplication)
class MobileApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'project', 'date_released', 'display_icon')
    list_filter = ('date_released', 'project')
    search_fields = ('name', 'description', 'project__title')
    autocomplete_fields = ['project']

    def display_icon(self, obj):
        return format_html('<img src="{}" width="30" height="30" />', obj.icon.url)
    display_icon.short_description = 'Icon'

@admin.register(DesktopApplication)
class DesktopApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'project', 'date_released', 'display_icon')
    list_filter = ('date_released', 'project')
    search_fields = ('name', 'description', 'project__title')
    autocomplete_fields = ['project']

    def display_icon(self, obj):
        return format_html('<img src="{}" width="30" height="30" />', obj.icon.url)
    display_icon.short_description = 'Icon'

@admin.register(WebApplication)
class WebApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_icon', 'project', 'url_link')
    search_fields = ('name', 'url', 'project__title')
    autocomplete_fields = ['project']

    def display_icon(self, obj):
        return format_html('<img src="{}" width="30" height="30" />', obj.icon.url)
    display_icon.short_description = 'Icon'

    def url_link(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', obj.url, obj.url)
    url_link.short_description = 'URL'

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('title', 'description_preview')
    search_fields = ('title', 'description')

    def description_preview(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    description_preview.short_description = 'Description Preview'

@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email', 'phone_number', 'location')
    search_fields = ('company_name', 'email', 'location')

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('years_of_experience', 'no_of_clients', 'no_of_complete_projects', 'no_of_workers')

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_image')

    def display_image(self, obj):
        return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
    display_image.short_description = 'Image Preview'

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'job_title', 'display_photo', 'comment_preview')
    search_fields = ('name', 'job_title', 'comment')

    def display_photo(self, obj):
        return format_html('<img src="{}" width="50" height="50" />', obj.user_photo.url)
    display_photo.short_description = 'Photo'

    def comment_preview(self, obj):
        return obj.comment[:100] + '...' if len(obj.comment) > 100 else obj.comment
    comment_preview.short_description = 'Comment Preview'

@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ('title', 'agreement_type', 'project', 'date_published')
    list_filter = ('agreement_type', 'date_published')
    search_fields = ('title', 'description', 'project__title')
    autocomplete_fields = ['project']

@admin.register(TechStack)
class TechStackAdmin(admin.ModelAdmin):
    list_display = ('language',)
    search_fields = ('language',)