from django.urls import path
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    student_signup,
    student_login,
    student_logout,
    student_dashboard,
    apply,
    load_constituencies,
    load_wards,
    load_polling_stations,
    request_password_reset,
    verify_reset_otp,
    set_new_password,
)

# ------------------------
# Root redirect
# ------------------------
def root_redirect(request):
    # Always send to student login
    return redirect('student_login')


# ------------------------
# URL patterns
# ------------------------
urlpatterns = [
    path('', root_redirect, name='root_redirect'),

    path('signup/', student_signup, name='student_signup'),
    path('login/', student_login, name='student_login'),
    path('logout/', student_logout, name='student_logout'),
    path('dashboard/', student_dashboard, name='student_dashboard'),
    path('apply/', apply, name='apply'),

    # AJAX endpoints
    path('ajax/load-constituencies/', load_constituencies, name='load_constituencies'),
    path('ajax/load-wards/', load_wards, name='load_wards'),
    path('ajax/load-polling-stations/', load_polling_stations, name='load_polling_stations'),

    # Password reset flow
    path('reset-password/', request_password_reset, name='request_password_reset'),
    path('verify-reset-otp/', verify_reset_otp, name='verify_reset_otp'),
    path('set-new-password/', set_new_password, name='set_new_password'),
]