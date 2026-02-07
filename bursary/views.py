from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import ApplicationForm, StudentSignUpForm, StudentLoginForm
from .models import Application, Constituency

# ------------------------
# STUDENT AUTH
# ------------------------

def student_signup(request):
    """
    Allow a student to create an account.
    Admission number will be used as username by default.
    """
    if request.method == "POST":
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Signup successful! Welcome to the bursary portal.")
            return redirect('student_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudentSignUpForm()
    return render(request, 'bursary/student_signup.html', {'form': form})


def student_login(request):
    """
    Student login using username (admission number) and password.
    """
    if request.method == "POST":
        form = StudentLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('student_dashboard')
        else:
            messages.error(request, "Invalid credentials. Please try again.")
    else:
        form = StudentLoginForm()
    return render(request, 'bursary/student_login.html', {'form': form})


@login_required
def student_logout(request):
    """
    Log out the student and redirect to login page.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('student_login')


# ------------------------
# STUDENT DASHBOARD
# ------------------------
@login_required
def student_dashboard(request):
    """
    Dashboard shows all applications submitted by the logged-in student.
    """
    applications = Application.objects.filter(student_user=request.user)
    return render(request, 'bursary/student_dashboard.html', {'applications': applications})

@login_required
def apply(request):
    """
    View for students to submit bursary application with full validation.
    """
    extra_errors = {}

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)

        # -----------------------
        # LOCATION SECTION
        # -----------------------
        if not request.POST.get("county"):
            form.add_error("county", "Please select your county.")

        if not request.POST.get("constituency"):
            form.add_error("constituency", "Please select your constituency.")

        if not request.POST.get("level_of_study"):
            form.add_error("level_of_study", "Please select your level of study.")

        # -----------------------
        # PERSONAL DETAILS
        # -----------------------
        if not request.POST.get("full_name"):
            form.add_error("full_name", "Full name is required.")

        if not request.POST.get("gender"):
            extra_errors["gender"] = "Please select your gender."

        id_no = request.POST.get("id_no")
        birth_cert_no = request.POST.get("birth_cert_no")
        if not id_no and not birth_cert_no:
            extra_errors["id_no"] = "Enter either ID number or Birth Certificate number."

        if "identity_document" not in request.FILES:
            extra_errors["identity_document"] = "Please upload ID or Birth Certificate."

        # Disability logic
        if request.POST.get("disability") == "yes":
            if not request.POST.get("disability_type"):
                extra_errors["disability_type"] = "Please specify type of disability."
            if "disability_document" not in request.FILES:
                extra_errors["disability_document"] = "Please upload supporting evidence for disability."

        # -----------------------
        # EDUCATION DETAILS
        # -----------------------
        required_education_fields = [
            "admission_number", "school", "course", "year_of_study",
            "amount_requested", "document"
        ]
        for field in required_education_fields:
            if not request.POST.get(field) and not request.FILES.get(field):
                form.add_error(field, f"{field.replace('_', ' ').capitalize()} is required.")

        # -----------------------
        # GEO DETAILS
        # -----------------------
        geo_fields = ["polling_station", "sub_location", "location", "ward"]
        for field in geo_fields:
            if not request.POST.get(field):
                extra_errors[field] = f"{field.replace('_', ' ').capitalize()} is required."

        # -----------------------
        # FAMILY STATUS
        # -----------------------
        family_status = request.POST.get("family_status")
        if not family_status:
            extra_errors["family_status"] = "Please select your family status."
        else:
            # Depending on the status, check all fields under that section
            status_fields = []
            if family_status == "both_alive":
                status_fields = [
                    "father_name","father_phone","father_occupation","father_id",
                    "mother_name","mother_phone","mother_occupation","mother_id"
                ]
            elif family_status == "mother_dead":
                status_fields = [
                    "mother_name","mother_phone","mother_occupation","mother_id_copy",
                    "father_death_no","father_death_doc"
                ]
            elif family_status == "father_dead":
                status_fields = [
                    "father_name","father_phone","father_occupation","father_id_copy",
                    "mother_death_no","mother_death_doc"
                ]
            elif family_status == "single_mother":
                status_fields = ["mother_name","mother_phone","mother_occupation","mother_id_copy"]
            elif family_status == "single_father":
                status_fields = ["father_name","father_phone","father_occupation","father_id_copy"]
            elif family_status == "orphan":
                status_fields = [
                    "father_death_no","father_death_doc",
                    "mother_death_no","mother_death_doc",
                    "guardian_name","guardian_phone","guardian_occupation"
                ]
            for field in status_fields:
                if not request.POST.get(field) and not request.FILES.get(field):
                    extra_errors[field] = f"{field.replace('_', ' ').capitalize()} is required."

        # -----------------------
        # SIBLINGS
        # -----------------------
        siblings_count = request.POST.get("siblings_count")
        if not siblings_count:
            extra_errors["siblings_count"] = "Please enter number of siblings."
        # Table is optional → no further validation

        # -----------------------
        # REFEREES
        # -----------------------
        referee_fields = ["referee1_name","referee1_phone","referee2_name","referee2_phone"]
        for field in referee_fields:
            if not request.POST.get(field):
                extra_errors[field] = f"{field.replace('_', ' ').capitalize()} is required."

        # -----------------------
        # FINAL CHECK
        # -----------------------
        if form.is_valid() and not extra_errors:
            application = form.save(commit=False)
            application.student_user = request.user
            application.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('student_dashboard')

        messages.error(request, "Please correct the errors highlighted below.")

    else:
        form = ApplicationForm()

    return render(
        request,
        'bursary/apply.html',
        {
            'form': form,
            'errors': extra_errors
        }
    )

        # Disability conditional validation
        if request.POST.get("disability") == "yes":
            if not request.POST.get("disability_type"):
                extra_errors["disability_type"] = "Please specify the type of disability."
            if "disability_document" not in request.FILES:
                extra_errors["disability_document"] = "Please upload disability supporting evidence."

        # ---------- FINAL CHECK ----------
        if form.is_valid() and not extra_errors:
            application = form.save(commit=False)
            application.student_user = request.user
            application.save()

            messages.success(request, "Application submitted successfully.")
            return redirect('student_dashboard')

        messages.error(request, "Please correct the errors highlighted below.")

    else:
        form = ApplicationForm()

    return render(
        request,
        'bursary/apply.html',
        {
            'form': form,
            'errors': extra_errors
        }
    )

# ------------------------
# AJAX: Load Constituencies
# ------------------------

def load_constituencies(request):
    """
    AJAX call: returns list of constituencies for a given county.
    """
    county_id = request.GET.get('county')
    constituencies = Constituency.objects.filter(county_id=county_id)
    return JsonResponse(list(constituencies.values('id', 'name')), safe=False)
