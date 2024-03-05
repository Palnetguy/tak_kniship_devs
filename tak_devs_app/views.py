# views.py

from rest_framework import generics

from tak_web.settings import EMAIL_HOST_USER
from .models import Project, TeamMember, Testimonial, Gallery, FAQ, ContactUsMessage, WorkExperience, MobileApplication, DesktopApplication, WebApplication
from .serializers import ProjectSerializer, TeamMemberSerializer, TestimonialSerializer, GallerySerializer, FAQSerializer, ContactUsMessageSerializer, WorkExperienceSerializer, MobileApplicationSerializer, DesktopApplicationSerializer, WebApplicationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework_api_key.permissions import HasAPIKey
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class ProjectListView(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [HasAPIKey]


class ProjectDetailWithApplicationsView(generics.RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['mobile_applications'] = MobileApplication.objects.filter(project=self.get_object())
        context['desktop_applications'] = DesktopApplication.objects.filter(project=self.get_object())
        context['web_applications'] = WebApplication.objects.filter(project=self.get_object())
        print(context)
        return context


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
    # permission_classes = [HasAPIKey]

    def perform_create(self, serializer):
        # Extract data from the request
        name = self.request.data.get('name')
        subject = self.request.data.get('subject')
        email = self.request.data.get('email')
        message = self.request.data.get('message')
        phone_number = self.request.data.get('phone_number')

        print(name)
        print(subject)
        print(message)
        print(email)

        # Create a ContactUsMessage instance
        contact_us_message = ContactUsMessage(
            name=name,
            subject=subject,
            email=email,
            message=message,
            phone_number=phone_number
        )

        # Save the ContactUsMessage
        contact_us_message.save()

        # Send email notification
        send_contact_us_notification(contact_us_message)

def send_contact_us_notification(contact_us_message):
    # Compose the email subject and message
    subject = 'New Contact Us Message'
    # message = render_to_string('email/contact_us_notification_email.html', {'contact_us_message': contact_us_message})
    # plain_message = strip_tags(message)

    # Send the email
    send_mail(
        subject,
        "Trying Out stuff",
        "telxul@gmail.com",  # Sender's email address
        ['tusingwiremartinrhinetreviz@gmail.com'],  # Recipient's email address
        # html_message=message,
    )

class WorkExperienceDetailView(generics.ListAPIView):
    queryset = WorkExperience.objects.all()
    serializer_class = WorkExperienceSerializer
    permission_classes = [HasAPIKey]

class MobileApplicationListView(generics.ListAPIView):
    queryset = MobileApplication.objects.all()
    serializer_class = MobileApplicationSerializer
    permission_classes = [HasAPIKey]

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return MobileApplication.objects.filter(project__id=project_id)

class DesktopApplicationListView(generics.ListAPIView):
    queryset = DesktopApplication.objects.all()
    serializer_class = DesktopApplicationSerializer
    permission_classes = [HasAPIKey]

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return DesktopApplication.objects.filter(project__id=project_id)

class WebApplicationListView(generics.ListAPIView):
    queryset = WebApplication.objects.all()
    serializer_class = WebApplicationSerializer
    permission_classes = [HasAPIKey]

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return WebApplication.objects.filter(project__id=project_id)
