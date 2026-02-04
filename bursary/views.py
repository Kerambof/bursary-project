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
    applications = Application.objects.filter(admission_number=request.user.username)
    return render(request, 'bursary/student_dashboard.html', {'applications': applications})

# ------------------------
# BURSARY APPLICATION
# ------------------------

@login_required
def apply(request):
    """
    Students apply for bursary. Admission number is automatically assigned.
    """
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            # Link application to student
            application.admission_number = request.user.username
            application.full_name = f"{request.user.first_name} {request.user.last_name}"
            application.save()
            return redirect('success')
    else:
        form = ApplicationForm()
    return render(request, 'bursary/index.html', {'form': form})

def success(request):
    """
    Simple success page after submitting application.
    """
    return render(request, 'bursary/success.html')

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
