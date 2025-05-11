from rest_framework import serializers
from .models import Agreement, ContactInfo, Project, TeamMember, TechStack, Testimonial, Gallery, FAQ, ContactUsMessage, WorkExperience, MobileApplication, DesktopApplication, WebApplication, ProjectFeature, ProjectClient, ProjectImage


class TeamMemberSerializer(serializers.ModelSerializer):
    # profile_picture =  serializers.CharField(source='profile_picture.public_id', read_only=True)
    class Meta:
        model = TeamMember
        fields = '__all__'

class TestimonialSerializer(serializers.ModelSerializer):
    # user_photo = serializers.CharField(source='user_photo.public_id', read_only=True)
    class Meta:
        model = Testimonial
        fields = '__all__'

class GallerySerializer(serializers.ModelSerializer):
    # image = serializers.CharField(source='image.public_id', read_only=True)
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
    # icon = serializers.CharField(source='icon.public_id', read_only=True)
    class Meta:
        model = MobileApplication
        fields = '__all__'

class DesktopApplicationSerializer(serializers.ModelSerializer):
    # icon = serializers.CharField(source='icon.public_id', read_only=True)
    class Meta:
        model = DesktopApplication
        fields = '__all__'

class WebApplicationSerializer(serializers.ModelSerializer):
    # icon = serializers.CharField(source='icon.public_id', read_only=True)
    class Meta:
        model = WebApplication
        fields = '__all__'

class TechStackSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechStack
        fields = ('id', 'language')

class ProjectFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFeature
        fields = ('id', 'title', 'description')

class ProjectClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectClient
        fields = ('id', 'name', 'location', 'rating', 'message', 'profile_image')

class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = ('id', 'image', 'image_type', 'caption', 'order')

class ProjectSerializer(serializers.ModelSerializer):
    mobile_applications = MobileApplicationSerializer(many=True, read_only=True)
    desktop_applications = DesktopApplicationSerializer(many=True, read_only=True)
    web_applications = WebApplicationSerializer(many=True, read_only=True)
    tech_stack = TechStackSerializer(many=True, read_only=True)
    features = ProjectFeatureSerializer(many=True, read_only=True)
    client = ProjectClientSerializer(read_only=True)
    images = ProjectImageSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = (
            'id', 
            'title', 
            'project_category', 
            'images',
            'tech_stack', 
            'quote', 
            'about_project', 
            'challenges_faced',
            'date_published', 
            'duration_of_development', 
            'features', 
            'client',
            'mobile_applications',
            'desktop_applications',
            'web_applications'
        )

class AgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agreement
        fields = '__all__'