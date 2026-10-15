from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator


# Custom User Model
class CustomUser(AbstractUser):

    class UserType(models.TextChoices):
        RECRUITER = "RECRUITER", "Recruiter"
        JOBSEEKER = "JOBSEEKER", "Jobseeker"

    display_name = models.CharField(
        max_length=50,
        verbose_name="Display Name"
    )

    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name="Email Address"
    )

    user_type = models.CharField(
        max_length=50,
        choices=UserType.choices,
        verbose_name="User Type"
    )

    def __str__(self):
        return self.display_name or self.username


# Skill Model
class Skill(models.Model):

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Skills"


# Category Model
class Category(models.Model):

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"


# Recruiter Profile Model
class RecruiterProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recruiter_profile"
    )

    company_name = models.CharField(max_length=100)
    company_description = models.TextField(blank=True)
    company_website = models.URLField(blank=True)
    company_address = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} - {self.user.username}"


# Job Seeker Profile Model
class JobSeekerProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jobseeker_profile"
    )

    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=200, blank=True)

    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name="jobseekers"
    )

    resume = models.FileField(
        upload_to="resumes/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.display_name} - Jobseeker"


# Job Model
class Job(models.Model):

    class EmploymentType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full Time"
        PART_TIME = "PART_TIME", "Part Time"
        CONTRACT = "CONTRACT", "Contract"
        INTERNSHIP = "INTERNSHIP", "Internship"

    class JobStatus(models.TextChoices):
        OPEN = "OPEN", "Open"
        CLOSED = "CLOSED", "Closed"

    recruiter = models.ForeignKey(
        RecruiterProfile,
        on_delete=models.CASCADE,
        related_name="jobs"
    )

    title = models.CharField(max_length=200)

    number_of_openings = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="jobs"
    )

    description = models.TextField()

    required_skills = models.ManyToManyField(
        Skill,
        related_name="jobs"
    )

    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME
    )

    job_status = models.CharField(
        max_length=10,
        choices=JobStatus.choices,
        default=JobStatus.OPEN
    )

    location = models.CharField(max_length=200, blank=True)

    salary_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )

    salary_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )

    is_active = models.BooleanField(default=True)
    is_remote = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]


# Job Application Model
class JobApplication(models.Model):

    class ApplicationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        REVIEWING = "REVIEWING", "Reviewing"
        SHORTLISTED = "SHORTLISTED", "Shortlisted"
        REJECTED = "REJECTED", "Rejected"
        ACCEPTED = "ACCEPTED", "Accepted"

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    jobseeker = models.ForeignKey(
        JobSeekerProfile,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    cover_letter = models.TextField(blank=True)

    resume = models.FileField(
        upload_to="application_resumes/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING
    )

    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["job", "jobseeker"],
                name="unique_jobseeker_job_application"
            )
        ]

    def __str__(self):
        return f"{self.jobseeker.user.username} - {self.job.title}"