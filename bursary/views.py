from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
import traceback  # <-- added for debug

#password reset imports
import random
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import PasswordResetOTP
import traceback
import socket
socket.setdefaulttimeout(15)

from .forms import ApplicationForm, StudentSignUpForm, StudentLoginForm
from .models import Application, Constituency
from .models import Ward, PollingStation

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
        try:
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

    except Exception as e:
        # Print full traceback in console for debugging
        print("=== APPLY VIEW ERROR ===")
        traceback.print_exc()

        # Show error in template (for debug only)
        return render(
            request,
            'bursary/apply.html',
            {
                'form': ApplicationForm(),
                'errors': {'__all__': f"Server Error: {e}"},
                'application': None
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
def load_wards(request):
    constituency_id = request.GET.get('constituency')

    wards = Ward.objects.filter(
        constituency_id=constituency_id
    ).values('id', 'name')

    return JsonResponse(list(wards), safe=False)


def load_polling_stations(request):
    ward_id = request.GET.get('ward')

    polling = PollingStation.objects.filter(
        ward_id=ward_id
    ).values('id', 'name')

    return JsonResponse(list(polling), safe=False)

#password reset views would go here (not implemented in this snippet)
def request_password_reset(request):

    if request.method == "POST":

        try:

            print("===== PASSWORD RESET STARTED =====")

            email = request.POST.get("email")
            print("EMAIL ENTERED:", email)

            user = User.objects.get(email=email)
            print("USER FOUND:", user.username)

            # generate OTP
            otp = str(random.randint(100000, 999999))
            print("OTP GENERATED:", otp)

            # save OTP
            otp_obj = PasswordResetOTP.objects.create(
                user=user,
                otp=otp
            )

            print("OTP SAVED:", otp_obj.id)
            print("CONNECTING TO GMAIL SMTP...")
            # send email
            send_mail(
                subject="Password Reset Code",
                message=f"Your password reset verification code is: {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            print("EMAIL SENT SUCCESSFULLY")

            request.session['reset_user_id'] = user.id

            messages.success(request, "Verification code sent to your email.")

            return redirect('verify_reset_otp')

        except Exception as e:

            print("===== PASSWORD RESET ERROR =====")
            traceback.print_exc()

            messages.error(request, f"DEBUG ERROR: {str(e)}")

            return render(
                request,
                'bursary/request_password_reset.html',
                {
                    'debug_error': str(e)
                }
            )

    return render(request, 'bursary/request_password_reset.html')

# Additional views for OTP verification and password reset would go here (not implemented in this snippet)
def verify_reset_otp(request):
    user_id = request.session.get('reset_user_id')

    if not user_id:
        return redirect('request_password_reset')

    if request.method == "POST":
        entered_otp = request.POST.get("otp")

        try:
            otp_obj = PasswordResetOTP.objects.filter(
                user_id=user_id,
                otp=entered_otp,
                is_verified=False
            ).latest('created_at')

            if otp_obj.is_expired():
                messages.error(request, "Code expired. Request a new one.")
                return redirect('request_password_reset')

            otp_obj.is_verified = True
            otp_obj.save()

            request.session['otp_verified'] = True
            return redirect('set_new_password')

        except PasswordResetOTP.DoesNotExist:
            messages.error(request, "Invalid verification code.")

    return render(request, 'bursary/verify_reset_otp.html')
#set new password view would go here (not implemented in this snippet)
def set_new_password(request):
    user_id = request.session.get('reset_user_id')
    otp_verified = request.session.get('otp_verified')

    if not user_id or not otp_verified:
        return redirect('request_password_reset')

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('set_new_password')

        user = User.objects.get(id=user_id)
        user.set_password(password1)
        user.save()

        # clear session
        request.session.pop('reset_user_id', None)
        request.session.pop('otp_verified', None)

        messages.success(request, "Password reset successful. Please login.")
        return redirect('student_login')

    return render(request, 'bursary/set_new_password.html')