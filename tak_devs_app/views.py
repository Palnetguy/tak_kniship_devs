# views.py

from django.shortcuts import get_object_or_404, render, redirect
from rest_framework import generics

from tak_web.settings import EMAIL_HOST_USER
from .models import Agreement, ContactInfo, Project, ProjectClient, TeamMember, Testimonial, Gallery, FAQ, ContactUsMessage, WorkExperience, MobileApplication, DesktopApplication, WebApplication
from .serializers import AgreementSerializer, ContactInfoSeriliazer, ProjectSerializer, TeamMemberSerializer, TestimonialSerializer, GallerySerializer, FAQSerializer, ContactUsMessageSerializer, WorkExperienceSerializer, MobileApplicationSerializer, DesktopApplicationSerializer, WebApplicationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework_api_key.permissions import HasAPIKey
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from drf_yasg.utils import swagger_auto_schema
from django.contrib import messages
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from .forms import TestimonialForm, ProjectClientFeedbackForm
from django.conf import settings

from django.http import HttpResponse


def health_check(request):
    return HttpResponse("OK", status=200)

class ProjectListView(generics.ListAPIView):
    """
    Lists all projects with their features, tech stack, and client information.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    @swagger_auto_schema(
        operation_description="Get a list of all projects",
        responses={200: ProjectSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ProjectDetailView(generics.RetrieveAPIView):
    """
    Retrieves details for a specific project.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    @swagger_auto_schema(
        operation_description="Get details of a specific project",
        responses={200: ProjectSerializer()}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ProjectDetailWithApplicationsView(generics.RetrieveAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [HasAPIKey]

    def get_queryset(self):
        return Project.objects.prefetch_related(
            'tech_stack',
            'mobile_applications',  # Changed from mobileapplication_set
            'desktop_applications',  # Changed from desktopapplication_set
            'web_applications',     # Changed from webapplication_set
            'features',            # Added features
            'client'              # Added client
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
    serializer_class = TeamMemberSerializer
    permission_classes = [HasAPIKey]
    
    def get_queryset(self):
        # Explicitly order by 'order' field and then by 'name'
        return TeamMember.objects.all().order_by('order', 'name')

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
        [contact_us_message.email],  # Recipient's email address
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
    

def testimonial_form(request, token=None):
    form_submitted = False
    
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form_submitted = True
    else:
        form = TestimonialForm()
    
    return render(request, 'testimonial_form.html', {
        'form': form,
        'form_submitted': form_submitted
    })

def client_feedback_form(request, project_id, token=None):
    project = get_object_or_404(Project, pk=project_id)
    form_submitted = False
    
    # Verify token
    signer = TimestampSigner()
    try:
        value = signer.unsign(token, max_age=60*60*24*7)  # Valid for 7 days
        if str(project_id) != value:
            messages.error(request, "Invalid token. Please request a new feedback link.")
            return redirect('home')
    except (BadSignature, SignatureExpired):
        messages.error(request, "This feedback link has expired or is invalid.")
        return redirect('home')
    
    if request.method == 'POST':
        form = ProjectClientFeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            client = form.save(commit=False)
            client.project = project
            client.save()
            form_submitted = True
    else:
        # Check if client feedback already exists
        try:
            client = ProjectClient.objects.get(project=project)
            form = ProjectClientFeedbackForm(instance=client)
            messages.info(request, "You've already submitted feedback for this project. You can update it below.")
        except ProjectClient.DoesNotExist:
            form = ProjectClientFeedbackForm()
    
    return render(request, 'client_feedback_form.html', {
        'form': form,
        'project': project,
        'form_submitted': form_submitted
    })

def generate_client_feedback_link(project):
    """Generate a secure link for client feedback"""
    signer = TimestampSigner()
    token = signer.sign(str(project.id))
    return token

def send_feedback_request_email(project, recipient_email, recipient_name):
    """Send an email with the client feedback link"""
    token = generate_client_feedback_link(project)
    feedback_url = reverse('client_feedback_form', kwargs={'project_id': project.id, 'token': token})
    absolute_url = settings.SITE_URL + feedback_url
    
    subject = f"We'd like your feedback on {project.title}"
    html_message = render_to_string('email/feedback_request_email.html', {
        'project': project,
        'recipient_name': recipient_name,
        'feedback_url': absolute_url
    })
    
    send_mail(
        subject,
        f"Please share your feedback about {project.title} at: {absolute_url}",
        settings.EMAIL_HOST_USER,
        [recipient_email],
        html_message=html_message,
        fail_silently=False,
    )
    return True
