from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

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
            return redirect('student_dashboard')
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
            return redirect('student_dashboard')
    else:
        form = StudentLoginForm()
    return render(request, 'bursary/student_login.html', {'form': form})

@login_required
def student_logout(request):
    logout(request)
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

# ------------------------
# BURSARY APPLICATION
# ------------------------

@login_required
def apply(request):
    """
    View for students to submit bursary application.
    """
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.student_user = request.user
            application.save()
            return redirect('student_dashboard')
    else:
        form = ApplicationForm()
    return render(request, 'bursary/apply.html', {'form': form})

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
