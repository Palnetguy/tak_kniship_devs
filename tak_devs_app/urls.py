# urls.py

from django.urls import path
from .views import (
    ProjectListView, TeamMemberListView, TestimonialListView,
    GalleryListView, FAQListView, ContactUsMessageCreateView,
    WorkExperienceDetailView, MobileApplicationListView,
    DesktopApplicationListView, WebApplicationListView
)

urlpatterns = [
    path('projects/', ProjectListView.as_view(), name='project-list'),
    path('team-members/', TeamMemberListView.as_view(), name='team-member-list'),
    path('testimonials/', TestimonialListView.as_view(), name='testimonial-list'),
    path('gallery/', GalleryListView.as_view(), name='gallery-list'),
    path('faqs/', FAQListView.as_view(), name='faq-list'),
    path('contact-us/', ContactUsMessageCreateView.as_view(), name='contact-us-create'),
    path('work-experience/', WorkExperienceDetailView.as_view(), name='work-experience-detail'),
    path('mobile-applications/', MobileApplicationListView.as_view(), name='mobile-application-list'),
    path('desktop-applications/', DesktopApplicationListView.as_view(), name='desktop-application-list'),
    path('web-applications/', WebApplicationListView.as_view(), name='web-application-list'),
]
