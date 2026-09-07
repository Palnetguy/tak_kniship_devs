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
        fields = ('id', 'name', 'subject', 'email', 'phone_number', 'message', 'date_sent')
        read_only_fields = ('id', 'date_sent')

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
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProjectImage
        fields = ('id', 'image', 'image_url', 'image_type', 'caption', 'order')

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

class ProjectSerializer(serializers.ModelSerializer):
    mobile_applications = MobileApplicationSerializer(many=True, read_only=True)
    desktop_applications = DesktopApplicationSerializer(many=True, read_only=True)
    web_applications = WebApplicationSerializer(many=True, read_only=True)
    tech_stack = TechStackSerializer(many=True, read_only=True)
    features = ProjectFeatureSerializer(many=True, read_only=True)
    client = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            'id', 
            'title', 
            'slug',
            'project_category', 
            'images',
            'tech_stack', 
            'quote', 
            'overview',
            'problem',
            'solution',
            'status',
            'about_project', 
            'challenges_faced',
            'date_published', 
            'duration_of_development', 
            'is_published',
            'features', 
            'client',
            'mobile_applications',
            'desktop_applications',
            'web_applications'
        )

    def get_images(self, obj):
        images = {}
        for project_image in obj.images.all():
            if project_image.image_type not in images and project_image.image:
                images[project_image.image_type] = project_image.image.url
        return {
            'background': images.get('background'),
            'about': images.get('about'),
            'challenge': images.get('challenge'),
        }

    def get_client(self, obj):
        try:
            client = obj.client
        except ProjectClient.DoesNotExist:
            return None
        if not client.is_published:
            return None
        return ProjectClientSerializer(client, context=self.context).data

class AgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agreement
        fields = '__all__'
