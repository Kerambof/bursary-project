from django.urls import path
from django.shortcuts import redirect
from .views import (
    student_signup,
    student_login,
    student_logout,
    student_dashboard,
    load_constituencies,
    apply,
)

# Simple root redirect view
def root_redirect(request):
    # Redirect to login page by default
    return redirect('student_login')

urlpatterns = [
    path('', root_redirect, name='root_redirect'),  # Root URL
    path('signup/', student_signup, name='student_signup'),
    path('', student_login, name='student_login'),
    path('logout/', student_logout, name='student_logout'),
    path('dashboard/', student_dashboard, name='student_dashboard'),
    path('apply/', apply, name='applsy'),
    path('ajax/load-constituencies/', load_constituencies, name='ajax_load_constituencies'),
]
