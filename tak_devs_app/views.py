# views.py

from rest_framework import generics
from .models import Project, TeamMember, Testimonial, Gallery, FAQ, ContactUsMessage, WorkExperience, MobileApplication, DesktopApplication, WebApplication
from .serializers import ProjectSerializer, TeamMemberSerializer, TestimonialSerializer, GallerySerializer, FAQSerializer, ContactUsMessageSerializer, WorkExperienceSerializer, MobileApplicationSerializer, DesktopApplicationSerializer, WebApplicationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework_api_key.permissions import HasAPIKey

class ProjectListView(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [HasAPIKey]

class TeamMemberListView(generics.ListAPIView):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    permission_classes = [HasAPIKey]

class TestimonialListView(generics.ListAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [HasAPIKey]

class GalleryListView(generics.ListAPIView):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    permission_classes = [HasAPIKey]

class FAQListView(generics.ListAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [HasAPIKey]

class ContactUsMessageCreateView(generics.CreateAPIView):
    queryset = ContactUsMessage.objects.all()
    serializer_class = ContactUsMessageSerializer
    permission_classes = [HasAPIKey]

class WorkExperienceDetailView(generics.RetrieveAPIView):
    queryset = WorkExperience.objects.all()
    serializer_class = WorkExperienceSerializer
    permission_classes = [HasAPIKey]

class MobileApplicationListView(generics.ListAPIView):
    queryset = MobileApplication.objects.all()
    serializer_class = MobileApplicationSerializer
    permission_classes = [HasAPIKey]

class DesktopApplicationListView(generics.ListAPIView):
    queryset = DesktopApplication.objects.all()
    serializer_class = DesktopApplicationSerializer
    permission_classes = [HasAPIKey]

class WebApplicationListView(generics.ListAPIView):
    queryset = WebApplication.objects.all()
    serializer_class = WebApplicationSerializer
    permission_classes = [HasAPIKey]
