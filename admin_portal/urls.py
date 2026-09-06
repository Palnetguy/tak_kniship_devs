from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CsrfView,
    CurrentUserView,
    DashboardView,
    LoginView,
    LogoutView,
    ProjectDetailView,
    ProjectListView,
    PortfolioProjectViewSet,
    TeamMemberViewSet,
    TestimonialViewSet,
    FAQViewSet,
    GalleryViewSet,
    ContactInfoViewSet,
    ContactMessageViewSet,
)

router = DefaultRouter()
router.register("portfolio", PortfolioProjectViewSet, basename="admin-portfolio")
router.register("team", TeamMemberViewSet, basename="admin-team")
router.register("testimonials", TestimonialViewSet, basename="admin-testimonials")
router.register("faqs", FAQViewSet, basename="admin-faqs")
router.register("media", GalleryViewSet, basename="admin-media")
router.register("contact-info", ContactInfoViewSet, basename="admin-contact-info")
router.register("messages", ContactMessageViewSet, basename="admin-messages")

urlpatterns = [
    path("auth/csrf/", CsrfView.as_view(), name="admin-csrf"),
    path("auth/login/", LoginView.as_view(), name="admin-login"),
    path("auth/logout/", LogoutView.as_view(), name="admin-logout"),
    path("auth/me/", CurrentUserView.as_view(), name="admin-current-user"),
    path("dashboard/", DashboardView.as_view(), name="admin-dashboard"),
    path("projects/", ProjectListView.as_view(), name="admin-projects"),
    path("projects/<slug:slug>/", ProjectDetailView.as_view(), name="admin-project-detail"),
    path("", include(router.urls)),
]
