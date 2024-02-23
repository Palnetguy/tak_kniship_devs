# urls.py

from django.urls import path
from .views import (
    ProjectDetailWithApplicationsView, ProjectListView, TeamMemberListView, TestimonialListView,
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
    path('project/<int:project_id>/mobile-applications/', MobileApplicationListView.as_view(), name='mobile-application-list'),
    path('project/<int:project_id>/desktop-applications/', DesktopApplicationListView.as_view(), name='desktop-application-list'),
    path('project/<int:project_id>/web-applications/', WebApplicationListView.as_view(), name='web-application-list'),
    # path('project/<int:pk>/', ProjectDetailWithApplicationsView.as_view(), name='project-detail-with-applications'),
]
