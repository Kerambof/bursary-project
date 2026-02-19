from django.urls import path
from django.shortcuts import redirect
from .views import (
    student_signup,
    student_login,
    student_logout,
    student_dashboard,
    apply,
    load_constituencies,
)

# ------------------------
# Root redirect
def root_redirect(request):
    # Always send to student login
    return redirect('student_login')

# ------------------------
# URL patterns
# ------------------------
urlpatterns = [
    path('', root_redirect, name='root_redirect'),  # Root URL handles login/dashboard redirect
    path('signup/', student_signup, name='student_signup'),
    path('login/', student_login, name='student_login'),
    path('logout/', student_logout, name='student_logout'),
    path('dashboard/', student_dashboard, name='student_dashboard'),
    path('apply/', apply, name='apply'),
    path('ajax/load-constituencies/', load_constituencies, name='ajax_load_constituencies'),
]
