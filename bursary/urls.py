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
    if request.user.is_authenticated:
        return redirect('student_dashboard')
    return redirect('student_login')

urlpatterns = [
    path('', root_redirect, name='root_redirect'),  # Root URL handles login/dashboard redirect
    path('signup/', student_signup, name='student_signup'),
    path('login/', student_login, name='student_login'),  # login now has a separate URL
    path('logout/', student_logout, name='student_logout'),
    path('dashboard/', student_dashboard, name='student_dashboard'),
    path('apply/', apply, name='applssy'),
    path('ajax/load-constituencies/', load_constituencies, name='ajax_load_constituencies'),
]
