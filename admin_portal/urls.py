from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CsrfView,
    CurrentUserView,
    ActivityListView,
    AdminAccountListView,
    AdminAccountDetailView,
    DashboardView,
    LoginView,
    LogoutView,
    ProjectDetailView,
    ProjectListView,
    WebsiteOverviewView,
    PublicWebsiteContentView,
    WebsiteContentViewSet,
    PortfolioProjectViewSet,
    TeamMemberViewSet,
    TestimonialViewSet,
    FAQViewSet,
    GalleryViewSet,
    ContactInfoViewSet,
    ContactMessageViewSet,
    ProjectImageViewSet,
    ProjectFeatureViewSet,
    ProjectClientViewSet,
    MobileApplicationViewSet,
    DesktopApplicationViewSet,
    WebApplicationViewSet,
    AgreementViewSet,
    WorkExperienceViewSet,
    FeedbackInvitationViewSet,
    ProjectFeedbackRequestView,
    DeploymentSettingsView,
)

router = DefaultRouter()
router.register("portfolio", PortfolioProjectViewSet, basename="admin-portfolio")
router.register("project-images", ProjectImageViewSet, basename="admin-project-images")
router.register("project-features", ProjectFeatureViewSet, basename="admin-project-features")
router.register("project-clients", ProjectClientViewSet, basename="admin-project-clients")
router.register("feedback-invitations", FeedbackInvitationViewSet, basename="admin-feedback-invitations")
router.register("mobile-applications", MobileApplicationViewSet, basename="admin-mobile-applications")
router.register("desktop-applications", DesktopApplicationViewSet, basename="admin-desktop-applications")
router.register("web-applications", WebApplicationViewSet, basename="admin-web-applications")
router.register("agreements", AgreementViewSet, basename="admin-agreements")
router.register("work-experience", WorkExperienceViewSet, basename="admin-work-experience")
router.register("team", TeamMemberViewSet, basename="admin-team")
router.register("testimonials", TestimonialViewSet, basename="admin-testimonials")
router.register("faqs", FAQViewSet, basename="admin-faqs")
router.register("media", GalleryViewSet, basename="admin-media")
router.register("contact-info", ContactInfoViewSet, basename="admin-contact-info")
router.register("messages", ContactMessageViewSet, basename="admin-messages")
router.register("website-content", WebsiteContentViewSet, basename="admin-website-content")

urlpatterns = [
    path("auth/csrf/", CsrfView.as_view(), name="admin-csrf"),
    path("auth/login/", LoginView.as_view(), name="admin-login"),
    path("auth/logout/", LogoutView.as_view(), name="admin-logout"),
    path("auth/me/", CurrentUserView.as_view(), name="admin-current-user"),
    path("dashboard/", DashboardView.as_view(), name="admin-dashboard"),
    path("settings/", DeploymentSettingsView.as_view(), name="admin-settings"),
    path("accounts/", AdminAccountListView.as_view(), name="admin-accounts"),
    path("accounts/<int:pk>/", AdminAccountDetailView.as_view(), name="admin-account-detail"),
    path("activity/", ActivityListView.as_view(), name="admin-activity"),
    path("website/overview/", WebsiteOverviewView.as_view(), name="website-overview"),
    path("public/website-content/<slug:key>/", PublicWebsiteContentView.as_view(), name="public-website-content"),
    path("projects/", ProjectListView.as_view(), name="admin-projects"),
    path("projects/<slug:slug>/", ProjectDetailView.as_view(), name="admin-project-detail"),
    path("portfolio/<int:pk>/request-feedback/", ProjectFeedbackRequestView.as_view(), name="admin-project-feedback-request"),
    path("", include(router.urls)),
]
