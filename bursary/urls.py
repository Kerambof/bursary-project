from django.urls import path
from .views import (
    apply, success, load_constituencies,
    student_signup, student_login, student_logout, student_dashboard
)

urlpatterns = [
    # Bursary application
    path('', apply, name='apply'),
    path('success/', success, name='success'),
    path('ajax/load-constituencies/', load_constituencies, name='ajax_load_constituencies'),

    # Student auth
    path('student-signup/', student_signup, name='student_signup'),
    path('student-login/', student_login, name='student_login'),
    path('student-logout/', student_logout, name='student_logout'),

    # Student dashboard
    path('dashboard/', student_dashboard, name='student_dashboard'),
]
