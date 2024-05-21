from rest_framework import serializers
from .models import ContactInfo, Project, TeamMember, TechStack, Testimonial, Gallery, FAQ, ContactUsMessage, WorkExperience, MobileApplication, DesktopApplication, WebApplication


class TeamMemberSerializer(serializers.ModelSerializer):
    profile_picture =  serializers.CharField(source='profile_picture.public_id', read_only=True)
    class Meta:
        model = TeamMember
        fields = '__all__'

class TestimonialSerializer(serializers.ModelSerializer):
    user_photo = serializers.CharField(source='user_photo.public_id', read_only=True)
    class Meta:
        model = Testimonial
        fields = '__all__'

class GallerySerializer(serializers.ModelSerializer):
    image = serializers.CharField(source='image.public_id', read_only=True)
    class Meta:
        model = Gallery
        fields = '__all__'

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'

class ContactUsMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUsMessage
        fields = '__all__'

class ContactInfoSeriliazer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = '__all__'

class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = '__all__'

class MobileApplicationSerializer(serializers.ModelSerializer):
    icon = serializers.CharField(source='icon.public_id', read_only=True)
    class Meta:
        model = MobileApplication
        fields = '__all__'

class DesktopApplicationSerializer(serializers.ModelSerializer):
    icon = serializers.CharField(source='icon.public_id', read_only=True)
    class Meta:
        model = DesktopApplication
        fields = '__all__'

class WebApplicationSerializer(serializers.ModelSerializer):
    icon = serializers.CharField(source='icon.public_id', read_only=True)
    class Meta:
        model = WebApplication
        fields = '__all__'

class TechStackSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechStack
        fields = ('language',)

class ProjectSerializer(serializers.ModelSerializer):
    mobile_applications = MobileApplicationSerializer(many=True, read_only=True)
    desktop_applications = DesktopApplicationSerializer(many=True, read_only=True)
    web_applications = WebApplicationSerializer(many=True, read_only=True)
    tech_stack = TechStackSerializer(many=True)
    project_background_image =  serializers.CharField(source='project_background_image.public_id', read_only=True)


    class Meta:
        model = Project
        fields = '__all__'