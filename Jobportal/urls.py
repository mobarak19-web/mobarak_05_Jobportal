from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [

    # Home & Dashboard
    path("", views.job_search, name="home"),
    path("jobs/", views.job_search, name="job_search"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # Authentication
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Profile
    path("profile/", views.Profile, name="Profile"),

    # Skills CRUD
    path("skills/", views.Skill_list, name="Skill_list"),
    path("skills/add/", views.Skill_create, name="Skill_create"),
    path("skills/<int:pk>/edit/", views.Skill_update, name="Skill_update"),
    path(
        "skills/<int:pk>/delete/",
        views.skill_delete,
        name="skill_delete",
    ),

    # Category CRUD
    path("categories/", views.Category_list, name="Category_list"),
    path(
        "categories/add/",
        views.Category_create,
        name="Category_create",
    ),
    path(
        "categories/<int:pk>/edit/",
        views.Category_update,
        name="Category_update",
    ),
    path(
        "categories/<int:pk>/delete/",
        views.Category_delete,
        name="Category_delete",
    ),

    # Job CRUD
    path("jobs/add/", views.job_create, name="job_create"),
    path("jobs/<int:pk>/", views.job_detail, name="job_detail"),
    path("jobs/<int:pk>/edit/", views.job_update, name="job_update"),
    path(
        "jobs/<int:pk>/applicants/",
        views.job_applicants,
        name="job_applicants",
    ),

    # Job Applications
    path(
        "jobs/<int:pk>/apply/",
        views.apply_job,
        name="apply_job",
    ),
    path(
        "my-applications/",
        views.my_applications,
        name="my_applications",
    ),
    path(
        "applications/<int:pk>/status/",
        views.update_application_status,
        name="update_application_status",
    ),

    # Matching System
    path(
        "matched-jobs/",
        views.matched_jobs,
        name="matched_jobs",
    ),
    path(
        "matched-candidates/",
        views.matched_candidates,
        name="matched_candidates",
    ),

]