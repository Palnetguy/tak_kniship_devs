from rest_framework import serializers
from .models import Project, TeamMember, Testimonial, Gallery, FAQ, ContactUsMessage, WorkExperience, MobileApplication, DesktopApplication, WebApplication

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = '__all__'

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = '__all__'

class GallerySerializer(serializers.ModelSerializer):
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

class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = '__all__'

class MobileApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileApplication
        fields = '__all__'

class DesktopApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesktopApplication
        fields = '__all__'

class WebApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebApplication
        fields = '__all__'
