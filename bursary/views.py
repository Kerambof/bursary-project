from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

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

    # 🚫 If admin already logged in, deny access
    if request.user.is_authenticated and (
        request.user.is_staff or request.user.is_superuser
    ):
        return HttpResponseForbidden("Use correct admin URL to login.")

    if request.method == "POST":
        form = StudentLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # 🚫 Prevent admin login via student login
            if user.is_staff or user.is_superuser:
                return HttpResponseForbidden("Use correct admin URL to Login")

            login(request, user)
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

    # 🚫 Admin completely denied
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Access denied.")

    applications = Application.objects.filter(
        student_user=request.user
    ).order_by('-created_at')

    full_name = f"{request.user.first_name} {request.user.last_name}".strip()
    student_full_name = full_name or request.user.get_username()

    context = {
        'applications': applications,
        'student_full_name': student_full_name
    }

    return render(request, 'bursary/student_dashboard.html', context)


@login_required
def apply(request):
    errors = {}
    try:
        # get the latest application for this student, if any
        application = request.user.applications.latest('created_at')
    except Application.DoesNotExist:
        application = None

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            app = form.save(commit=False)
            app.student_user = request.user

            # Save siblings as comma-separated strings
            names = request.POST.getlist('sibling_name[]')
            amounts = request.POST.getlist('sibling_amount[]')
            app.siblings_names = ", ".join(names)
            app.siblings_amounts = ", ".join(amounts)

            # -------------------------
            # Handle local file uploads
            # -------------------------
            uploaded_identity = request.FILES.get('identity_document')
            if uploaded_identity:
                app.identity_document = uploaded_identity

            uploaded_disability = request.FILES.get('disability_document')
            if uploaded_disability:
                app.disability_document = uploaded_disability

            uploaded_document = request.FILES.get('document')
            if uploaded_document:
                app.document = uploaded_document

            uploaded_transcript = request.FILES.get('transcript')
            if uploaded_transcript:
                app.transcript = uploaded_transcript

            uploaded_father_doc = request.FILES.get('father_death_doc')
            if uploaded_father_doc:
                app.father_death_doc = uploaded_father_doc

            uploaded_mother_doc = request.FILES.get('mother_death_doc')
            if uploaded_mother_doc:
                app.mother_death_doc = uploaded_mother_doc

            app.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('student_dashboard')
        else:
            messages.error(request, "Please fix the errors below.")
            errors = form.errors  # Pass errors to template

    else:
        form = ApplicationForm()

    return render(
        request,
        'bursary/apply.html',
        {
            'form': form,
            'errors': errors,
            'application': application  # <-- pass application to template
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