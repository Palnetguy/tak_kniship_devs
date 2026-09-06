from django.urls import path

from .views import (
    CsrfView,
    CurrentUserView,
    DashboardView,
    LoginView,
    LogoutView,
    ProjectDetailView,
    ProjectListView,
)

urlpatterns = [
    path("auth/csrf/", CsrfView.as_view(), name="admin-csrf"),
    path("auth/login/", LoginView.as_view(), name="admin-login"),
    path("auth/logout/", LogoutView.as_view(), name="admin-logout"),
    path("auth/me/", CurrentUserView.as_view(), name="admin-current-user"),
    path("dashboard/", DashboardView.as_view(), name="admin-dashboard"),
    path("projects/", ProjectListView.as_view(), name="admin-projects"),
    path("projects/<slug:slug>/", ProjectDetailView.as_view(), name="admin-project-detail"),
]
