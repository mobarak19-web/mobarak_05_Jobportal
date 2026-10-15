from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser,
    Skill,
    Category,
    RecruiterProfile,
    JobSeekerProfile,
    Job,
    JobApplication,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'display_name', 'email',
        'user_type', 'is_staff', 'is_active'
    )
    list_filter = ("user_type", "is_staff", "is_active")
    search_fields = ("username", "display_name", "email")
    ordering = ("username",)

    fieldsets = UserAdmin.fieldsets + (
        ('Job Portal Information', {
            'fields': ('display_name', 'user_type'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Job Portal Information', {
            'fields': ('display_name', 'email', 'user_type'),
        }),
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'company_name',
        'company_address', 'created_at'
    )
    search_fields = (
        'user__username', 'user__email', 'company_name'
    )
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'phone', 'address', 'created_at'
    )
    search_fields = (
        'user__username', 'user__email', 'phone', 'address'
    )
    list_filter = ('address', 'created_at')
    filter_horizontal = ('skills',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'recruiter', 'category',
        'number_of_openings', 'employment_type',
        'job_status', 'is_active', 'is_remote', 'created_at'
    )
    search_fields = (
        'title', 'description',
        'recruiter__company_name', 'category__name'
    )
    list_filter = (
        'category', 'employment_type',
        'job_status', 'is_active', 'created_at'
    )
    filter_horizontal = ('required_skills',)
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active', 'is_remote')
    date_hierarchy = 'created_at'


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'job', 'jobseeker', 'status', 'applied_at'
    )
    search_fields = (
        'job__title',
        'jobseeker__user__username',
        'jobseeker__user__email'
    )
    list_filter = ('status', 'applied_at')
    readonly_fields = ('applied_at', 'updated_at')
    list_editable = ('status',)
    date_hierarchy = 'applied_at'