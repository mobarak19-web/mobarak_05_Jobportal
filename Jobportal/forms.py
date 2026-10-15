from django import forms
from .models import *
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Choose a Username",
            "autocomplete": "username",
        })
    )

    display_name = forms.CharField(
        label="Display Name",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Display Name",
        })
    )

    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Email Account",
            "autocomplete": "email",
        })
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password",
        })
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm Password",
        })
    )

    user_type = forms.ChoiceField(
        choices=CustomUser.UserType.choices,
        label="Account Type",
        widget=forms.Select(attrs={
            "class": "form-select",
        })
    )

    class Meta:
        model = CustomUser
        fields = ["username", "display_name", "email", "password1", "password2", "user_type"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Choose a Username",
            "autocomplete": "username",
        })
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Input Password",
        })
    )

    def clean(self):
        cleaned_data = self.cleaned_data
        username_or_email = (cleaned_data.get("username") or "").strip()
        password = cleaned_data.get("password")

        if username_or_email and password:
            if "@" in username_or_email:
                try:
                    user_obj = CustomUser.objects.get(email__iexact=username_or_email)
                    username = user_obj.username
                except CustomUser.DoesNotExist:
                    raise forms.ValidationError("Invalid username or email.")
            else:
                username = username_or_email

            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password,
            )

            if self.user_cache is None:
                raise forms.ValidationError("Invalid username/email or Password.")
            else:
                self.confirm_login_allowed(self.user_cache)

        return cleaned_data


# Create a Skill form
class SkillForm(forms.ModelForm):
    name = forms.CharField(
        label="Skills Name",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. Python, Django, React, Project Management",
        })
    )

    class Meta:
        model = Skill
        fields = ["name"]

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Skill name is required.")
        return name


# Create a Category form
class CategoryForm(forms.ModelForm):
    name = forms.CharField(
        label="Skills Name",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. Technology, software_Engineear, Developer, Finance, Marketing",
        })
    )

    description = forms.CharField(
        label="Category Name",
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 4,
            "placeholder": "Provide a brief description of the types of jobs in this category...",
        })
    )

    class Meta:
        model = Category
        fields = ["name", "description"]

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Category name is required.")
        return name


# Create a RecruiterProfile Form
class RecruiterProfileForm(forms.ModelForm):
    company_name = forms.CharField(
        label="Company Name",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Your Company Name",
        })
    )

    company_website = forms.URLField(
        label="Company Website",
        required=False,
        widget=forms.URLInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Your Company Website",
        })
    )

    company_description = forms.CharField(
        label="Company Description",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 4,
            "placeholder": "Enter Your Company Description",
        })
    )

    company_address = forms.CharField(
        label="Company Address",
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Your Company Address",
        })
    )

    phone = forms.CharField(
        label="Phone",
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "type": "tel",
            "placeholder": "Enter Your Phone Number",
        })
    )

    class Meta:
        model = RecruiterProfile
        fields = [
            "company_name", "company_website", "company_description",
            "company_address", "phone",
        ]


# Create a JobSeekerProfile Form
class JobSeekerProfileForm(forms.ModelForm):
    phone = forms.CharField(
        label="Phone",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "type": "tel",
            "placeholder": "Enter Your Phone Number",
        })
    )

    address = forms.CharField(
        label="Address",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Your Address",
        })
    )

    bio = forms.CharField(
        label="Biography",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 4,
            "placeholder": "Enter Your Biography",
        })
    )

    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        label="Skills",
        widget=forms.CheckboxSelectMultiple(attrs={
            "class": "form-check-input",
        })
    )

    resume = forms.FileField(
        label="Resume",
        required=False,
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control",
        })
    )

    class Meta:
        model = JobSeekerProfile
        fields = ["phone", "address", "bio", "skills", "resume"]

    def clean_resume(self):
        resume = self.cleaned_data.get("resume")
        if resume and hasattr(resume, "size"):
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Resume must be 5 MB or smaller.")

            extension = resume.name.lower().rsplit(".", 1)[-1]
            if extension not in {"pdf", "doc", "docx"}:
                raise forms.ValidationError("Upload a PDF, DOC, or DOCX resume.")

        return resume


# Create a Job form
class JobForm(forms.ModelForm):
    title = forms.CharField(
        label="Job Title",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Job Title",
        })
    )

    number_of_openings = forms.IntegerField(
        label="Number of Openings",
        min_value=1,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Number of Vacancies",
        })
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Category",
        widget=forms.Select(attrs={
            "class": "form-select",
        })
    )

    description = forms.CharField(
        label="Job Description",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 5,
            "placeholder": "Enter Job Description",
        })
    )

    required_skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        label="Required Skills",
        widget=forms.CheckboxSelectMultiple(attrs={
            "class": "form-check-input",
        })
    )

    employment_type = forms.ChoiceField(
        label="Employment Type",
        choices=Job.EmploymentType.choices,
        widget=forms.Select(attrs={
            "class": "form-select",
        })
    )

    job_status = forms.ChoiceField(
        label="Job Status",
        choices=Job.JobStatus.choices,
        widget=forms.Select(attrs={
            "class": "form-select",
        })
    )

    location = forms.CharField(
        label="Location",
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. Dhaka, Bangladesh",
        })
    )

    salary_min = forms.DecimalField(
        label="Minimum Salary",
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Min Salary Amount",
        })
    )

    salary_max = forms.DecimalField(
        label="Maximum Salary",
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Max Salary Amount",
        })
    )

    is_remote = forms.BooleanField(
        label="Is Remote Job?",
        required=False,
        widget=forms.CheckboxInput(attrs={
            "class": "form-check-input",
        })
    )

    is_active = forms.BooleanField(
        label="Is Active?",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            "class": "form-check-input",
        })
    )

    class Meta:
        model = Job
        fields = [
            "title", "number_of_openings", "category", "description",
            "required_skills", "employment_type", "job_status", "location",
            "salary_min", "salary_max", "is_active", "is_remote",
        ]

    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get("salary_min")
        salary_max = cleaned_data.get("salary_max")

        if (
            salary_min is not None
            and salary_max is not None
            and salary_max < salary_min
        ):
            self.add_error(
                "salary_max",
                "Maximum salary cannot be less than minimum salary.",
            )

        return cleaned_data


class JobApplicationForm(forms.ModelForm):
    cover_letter = forms.CharField(
        label="Cover Letter",
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 6,
            "placeholder": "Write your professional cover letter here...",
        })
    )

    resume = forms.FileField(
        label="Upload Resume",
        required=True,
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control",
        })
    )

    class Meta:
        model = JobApplication
        fields = ["cover_letter", "resume"]

    def clean_resume(self):
        resume = self.cleaned_data.get("resume")
        if resume and hasattr(resume, "size"):
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Resume must be 5 MB or smaller.")

            extension = resume.name.lower().rsplit(".", 1)[-1]
            if extension not in {"pdf", "doc", "docx"}:
                raise forms.ValidationError("Upload a PDF, DOC, or DOCX resume.")

        return resume
