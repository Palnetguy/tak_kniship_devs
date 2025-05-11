# views.py

from django.shortcuts import get_object_or_404
from rest_framework import generics

from tak_web.settings import EMAIL_HOST_USER
from .models import Agreement, ContactInfo, Project, TeamMember, Testimonial, Gallery, FAQ, ContactUsMessage, WorkExperience, MobileApplication, DesktopApplication, WebApplication
from .serializers import AgreementSerializer, ContactInfoSeriliazer, ProjectSerializer, TeamMemberSerializer, TestimonialSerializer, GallerySerializer, FAQSerializer, ContactUsMessageSerializer, WorkExperienceSerializer, MobileApplicationSerializer, DesktopApplicationSerializer, WebApplicationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework_api_key.permissions import HasAPIKey
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.http import HttpResponse


def health_check(request):
    return HttpResponse("OK", status=200)

class ProjectListView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [HasAPIKey]

    def get_queryset(self):
        return Project.objects.prefetch_related(
            'tech_stack',
            'mobileapplication_set',
            'desktopapplication_set',
            'webapplication_set'
        ).all()


class ProjectDetailWithApplicationsView(generics.RetrieveAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [HasAPIKey]

    def get_queryset(self):
        return Project.objects.prefetch_related(
            'tech_stack',
            'mobileapplication_set',
            'desktopapplication_set',
            'webapplication_set'
        )

    
class PolicyDetailAgreement(generics.RetrieveAPIView):
    # queryset = Agreement.objects.all()
    serializer_class = AgreementSerializer
    permission_classes = [HasAPIKey]

    # def get_queryset(self):
    #     project_id = self.kwargs.get('project_id')
    #     return Agreement.objects.filter(project__id=project_id, agreement_type='Policy' )
    
    def get_object(self):
        project_id = self.kwargs.get('project_id')
        return get_object_or_404(Agreement, project__id=project_id, agreement_type='Policy')
    
class TermsDetailAgreement(generics.RetrieveAPIView):
    serializer_class = AgreementSerializer
    permission_classes = [HasAPIKey]

    def get_object(self):
        project_id = self.kwargs.get('project_id')
        return get_object_or_404(Agreement, project__id=project_id, agreement_type='Terms')
   


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

        # Send Client and Admins email notification
        send_contact_us_notification(contact_us_message)
        send_admin_message_notification(contact_us_message)

def send_contact_us_notification(contact_us_message):
    subject = "Welcome to TAK Kniship Devs"
    html_message = render_to_string('email/contact_us_notification_email.html', {'contact_us_message': contact_us_message})
    # plain_message = strip_tags(html_message)
    print(contact_us_message.message)
    # Send the email
    send_mail(
        subject,
       'Thank You for your Message. We will get back to you soon.',
        EMAIL_HOST_USER,  # Sender's email address
        ['tusingwiremartinrhinetreviz@gmail.com','sktechug@gmail.com'],  # Recipient's email address
        html_message=html_message,
    )

def send_admin_message_notification(contact_us_message):
    # message = render_to_string('email/contact_us_notification_email.html', {'contact_us_message': contact_us_message})
    # plain_message = strip_tags(message)
    print(contact_us_message.message)
    # Send the email
    send_mail(
        contact_us_message.subject,
        f"Hello,\n{contact_us_message.name} has sent a message:\n"
    f"Phone number: {contact_us_message.phone_number}\n"
    f"Message:\n{contact_us_message.message}",
        EMAIL_HOST_USER,  # Sender's email address
        ['tusingwiremartinrhinetreviz@gmail.com','sktechug@gmail.com'],  # Recipient's email address
        # html_message=message,
    )

class WorkExperienceDetailView(generics.ListAPIView):
    queryset = WorkExperience.objects.all()
    serializer_class = WorkExperienceSerializer
    permission_classes = [HasAPIKey]

class ContactInfoView(generics.ListAPIView):
    queryset = ContactInfo.objects.all()
    serializer_class = ContactInfoSeriliazer
    permission_classes = [HasAPIKey]

class MobileApplicationListView(generics.ListAPIView):
    serializer_class = MobileApplicationSerializer
    permission_classes = [HasAPIKey]

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return MobileApplication.objects.select_related('project').filter(project__id=project_id)

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
