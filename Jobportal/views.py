from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.contrib import messages

from .models import (
    CustomUser, Skill, Category, RecruiterProfile, JobSeekerProfile,
    Job, JobApplication,
)
from .forms import (
    RegistrationForm, LoginForm, SkillForm, CategoryForm,
    RecruiterProfileForm, JobSeekerProfileForm, JobForm, JobApplicationForm,
)


# Authentication

def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            if user.user_type == "RECRUITER":
                RecruiterProfile.objects.get_or_create(
                    user=user,
                    defaults={"company_name": f"{user.display_name}'s Company"},
                )
            else:
                JobSeekerProfile.objects.get_or_create(user=user)

            auth_login(request, user)
            messages.success(request, "Your account has been created successfully.")
            return redirect("dashboard")
    else:
        form = RegistrationForm()

    return render(request, "register.html", {"page": "Registration", "form": form})


def login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect("dashboard")
    else:
        form = LoginForm(request=request)

    return render(request, "login.html", {"page": "Login", "form": form})


@login_required(login_url="login")
def logout(request):
    auth_logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect("login")


# Skills: list is public; only staff can add, edit, or delete.

def Skill_list(request):
    skills = Skill.objects.order_by("name")
    return render(request, "Skill_list.html", {
        "page": "Skills List", "skills": skills,
    })


@login_required(login_url="login")
def Skill_create(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to add skills.")
        return redirect("Skill_list")

    form = SkillForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Skill created successfully.")
        return redirect("Skill_list")

    return render(request, "skill_form.html", {
        "page": "Skill Create", "form": form,
        "page_title": "Add Skill", "button_text": "Save Skill",
    })


@login_required(login_url="login")
def Skill_update(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to edit skills.")
        return redirect("Skill_list")

    form = SkillForm(request.POST or None, instance=skill)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Skill updated successfully.")
        return redirect("Skill_list")

    return render(request, "skill_form.html", {
        "page": "Skill Update", "form": form,
        "page_title": "Update Skill", "button_text": "Update Skill",
    })


@login_required(login_url="login")
@require_POST
def skill_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to delete skills.")
        return redirect("Skill_list")

    get_object_or_404(Skill, pk=pk).delete()
    messages.success(request, "Skill deleted successfully.")
    return redirect("Skill_list")


# Categories: list is public; only staff can add, edit, or delete.

def Category_list(request):
    categories = Category.objects.order_by("name")
    return render(request, "Category_list.html", {
        "page": "Category List", "categories": categories,
    })


@login_required(login_url="login")
def Category_create(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to add categories.")
        return redirect("Category_list")

    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category created successfully.")
        return redirect("Category_list")

    return render(request, "Category_form.html", {
        "page": "Category Create", "form": form,
        "page_title": "Add Job Category", "button_text": "Save Category",
    })


@login_required(login_url="login")
def Category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to edit categories.")
        return redirect("Category_list")

    form = CategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category updated successfully.")
        return redirect("Category_list")

    return render(request, "Category_form.html", {
        "page": "Category Update", "form": form,
        "page_title": "Update Job Category", "button_text": "Update Category",
    })


@login_required(login_url="login")
@require_POST
def Category_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to delete categories.")
        return redirect("Category_list")

    category = get_object_or_404(Category, pk=pk)
    if Job.objects.filter(category=category).exists():
        messages.error(request, "This category is being used by jobs and cannot be deleted.")
    else:
        category.delete()
        messages.success(request, "Category deleted successfully.")
    return redirect("Category_list")


# Dashboard

@login_required(login_url="login")
def dashboard(request):
    if request.user.user_type == "RECRUITER":
        jobs = Job.objects.filter(recruiter__user=request.user).select_related(
            "category", "recruiter"
        ).order_by("-created_at")
        return render(request, "dashboard.html", {
            "page": "Dashboard", "jobs": jobs, "total_jobs": jobs.count(),
        })

    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    applications = JobApplication.objects.filter(jobseeker=profile).select_related(
        "job", "job__category", "job__recruiter"
    ).order_by("-applied_at")
    return render(request, "dashboard.html", {
        "page": "Dashboard",
        "applications": applications,
        "total_applications": applications.count(),
    })


def require_user_type(request, user_type):
    if request.user.user_type != user_type:
        messages.error(request, "You do not have permission to access this page.")
        return redirect("dashboard")
    return None


# Profile

@login_required(login_url="login")
def Profile(request):
    if request.user.user_type == "RECRUITER":
        profile = get_object_or_404(RecruiterProfile, user=request.user)
        form_class = RecruiterProfileForm
    else:
        profile = get_object_or_404(JobSeekerProfile, user=request.user)
        form_class = JobSeekerProfileForm

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("Profile")
    else:
        form = form_class(instance=profile)

    return render(request, "profile_form.html", {
        "page": "Edit Profile", "form": form, "profile": profile,
    })


# Job create, update, delete, search, and detail

@login_required(login_url="login")
def job_create(request):
    denied = require_user_type(request, "RECRUITER")
    if denied:
        return denied

    recruiter_profile = get_object_or_404(RecruiterProfile, user=request.user)
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = recruiter_profile
            job.save()
            form.save_m2m()
            messages.success(request, "Job posted successfully.")
            return redirect("dashboard")
    else:
        form = JobForm()

    return render(request, "job_form.html", {
        "page": "Post a Job", "form": form, "button_text": "Post Job",
    })


@login_required(login_url="login")
def job_update(request, pk):
    denied = require_user_type(request, "RECRUITER")
    if denied:
        return denied

    job = get_object_or_404(Job, pk=pk, recruiter__user=request.user)
    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully.")
            return redirect("dashboard")
    else:
        form = JobForm(instance=job)

    return render(request, "job_form.html", {
        "page": "Update a Job", "form": form,
        "button_text": "Save Changes", "job": job,
    })


@login_required(login_url="login")
@require_POST
def job_delete(request, pk):
    denied = require_user_type(request, "RECRUITER")
    if denied:
        return denied
    job = get_object_or_404(Job, pk=pk, recruiter__user=request.user)
    job.delete()
    messages.success(request, "Job deleted successfully.")
    return redirect("dashboard")


def job_search(request):
    jobs = Job.objects.filter(
        is_active=True, job_status=Job.JobStatus.OPEN,
    ).select_related("category", "recruiter").prefetch_related("required_skills")

    search = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    skill_id = request.GET.get("skill", "").strip()

    if search:
        jobs = jobs.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(category__name__icontains=search)
            | Q(recruiter__company_name__icontains=search)
            | Q(required_skills__name__icontains=search)
        )
    if category_id.isdigit():
        jobs = jobs.filter(category_id=int(category_id))
    if skill_id.isdigit():
        jobs = jobs.filter(required_skills__id=int(skill_id))

    jobs = jobs.distinct()
    return render(request, "job_search.html", {
        "page": "Find Jobs", "jobs": jobs,
        "categories": Category.objects.all(), "skills": Skill.objects.all(),
        "search": search, "selected_category": category_id,
        "selected_skill": skill_id,
    })


def job_detail(request, pk):
    job = get_object_or_404(
        Job.objects.select_related("category", "recruiter").prefetch_related("required_skills"),
        pk=pk, is_active=True, job_status=Job.JobStatus.OPEN,
    )
    return render(request, "job_detail.html", {"page": job.title, "job": job})


# Job applications

@login_required(login_url="login")
def apply_job(request, pk):
    if request.user.user_type != "JOBSEEKER":
        messages.error(request, "Please log in as a job seeker to apply.")
        return redirect("dashboard")

    job = get_object_or_404(
        Job.objects.select_related("category", "recruiter"),
        pk=pk, is_active=True, job_status=Job.JobStatus.OPEN,
    )
    profile = get_object_or_404(JobSeekerProfile, user=request.user)

    if JobApplication.objects.filter(job=job, jobseeker=profile).exists():
        messages.warning(request, "You have already submitted an application for this position.")
        return redirect("job_detail", pk=job.pk)

    if request.method == "POST":
        form = JobApplicationForm(request.POST, request.FILES)
        form.fields["resume"].required = False
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.jobseeker = profile
            uploaded_resume = form.cleaned_data.get("resume")

            if not uploaded_resume:
                if not profile.resume:
                    form.add_error(
                        "resume",
                        "Please upload your resume or add it to your profile before applying.",
                    )
                else:
                    application.resume = profile.resume

            if not form.errors:
                try:
                    with transaction.atomic():
                        application.save()
                    messages.success(request, "Congratulations! Your application has been received.")
                    return redirect("my_applications")
                except IntegrityError:
                    messages.warning(request, "An application for this position already exists in your account.")
                    return redirect("job_detail", pk=job.pk)
    else:
        form = JobApplicationForm()
        form.fields["resume"].required = False

    return render(request, "apply_job.html", {
        "page": "Job Apply", "job": job, "form": form, "profile": profile,
    })


@login_required(login_url="login")
def my_applications(request):
    if request.user.user_type != "JOBSEEKER":
        messages.error(request, "Your account does not have permission to access job applications.")
        return redirect("dashboard")

    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    applications = JobApplication.objects.filter(jobseeker=profile).select_related(
        "job", "job__category", "job__recruiter"
    ).order_by("-applied_at")

    return render(request, "my_applications.html", {
        "page": "My Applications", "applications": applications,
    })


@login_required(login_url="login")
def job_applicants(request, pk):
    if request.user.user_type != "RECRUITER":
        messages.error(request, "Access denied. Only recruiters can check job applicants.")
        return redirect("dashboard")

    job = get_object_or_404(Job, pk=pk, recruiter__user=request.user)
    applications = JobApplication.objects.filter(job=job).select_related(
        "jobseeker", "jobseeker__user"
    ).prefetch_related("jobseeker__skills").order_by("-applied_at")

    return render(request, "job_applicants.html", {
        "page": "Applicants List", "job": job, "applications": applications,
    })


@login_required(login_url="login")
@require_POST
def update_application_status(request, pk):
    if request.user.user_type != "RECRUITER":
        messages.error(request, "You are not authorized to manage application statuses.")
        return redirect("dashboard")

    application = get_object_or_404(
        JobApplication.objects.select_related("job"),
        pk=pk, job__recruiter__user=request.user,
    )
    allowed_statuses = {value for value, label in JobApplication.ApplicationStatus.choices}
    new_status = request.POST.get("status", "")

    if new_status not in allowed_statuses:
        messages.error(request, "Please select a valid application status.")
    else:
        application.status = new_status
        application.save(update_fields=["status", "updated_at"])
        messages.success(request, "The applicant's status has been changed successfully.")

    return redirect("job_applicants", pk=application.job_id)


# Matching system

@login_required(login_url="login")
def matched_jobs(request):
    if request.user.user_type != "JOBSEEKER":
        messages.error(request, "This section is available only to registered job seekers.")
        return redirect("dashboard")

    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    applied_job_ids = JobApplication.objects.filter(
        jobseeker=profile,
    ).values_list("job_id", flat=True)

    jobs = Job.objects.filter(
        is_active=True,
        job_status=Job.JobStatus.OPEN,
        required_skills__in=profile.skills.all(),
    ).exclude(pk__in=applied_job_ids).annotate(
        matched_skill_count=Count(
            "required_skills",
            filter=Q(required_skills__in=profile.skills.all()),
            distinct=True,
        )
    ).select_related("category", "recruiter").prefetch_related(
        "required_skills"
    ).distinct().order_by("-matched_skill_count", "-created_at")

    return render(request, "matched_jobs.html", {
        "page": "Recommended Jobs", "jobs": jobs, "profile": profile,
    })


@login_required(login_url="login")
def matched_candidates(request, pk):
    if request.user.user_type != "RECRUITER":
        messages.error(request, "Only recruiters can view matched candidates.")
        return redirect("dashboard")

    job = get_object_or_404(
        Job.objects.prefetch_related("required_skills"),
        pk=pk, recruiter__user=request.user,
    )
    candidates = JobSeekerProfile.objects.filter(
        skills__in=job.required_skills.all(),
    ).annotate(
        matched_skill_count=Count(
            "skills",
            filter=Q(skills__in=job.required_skills.all()),
            distinct=True,
        )
    ).select_related("user").prefetch_related("skills").distinct().order_by(
        "-matched_skill_count"
    )

    return render(request, "matched_candidates.html", {
        "page": "Matched Candidates", "job": job, "candidates": candidates,
    })
