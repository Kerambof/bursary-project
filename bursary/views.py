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
    errors = {}
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

            app.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('student_dashboard')
        else:
            messages.error(request, "Please fix the errors below.")
            errors = form.errors  # Pass errors to template

    else:
        form = ApplicationForm()

    return render(request, 'bursary/apply.html', {'form': form, 'errors': errors})
 
 
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
