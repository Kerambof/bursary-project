from django.urls import path
from .views import (
    student_signup,
    student_login,
    student_logout,
    student_dashboard,
    load_constituencies,
    apply,  # now exists
)

urlpatterns = [
    path('signup/', student_signup, name='student_signup'),
    path('login/', student_login, name='student_login'),
    path('logout/', student_logout, name='student_logout'),
    path('dashboard/', student_dashboard, name='student_dashboard'),
    path('apply/', apply, name='apply'),
    path('ajax/load-constituencies/', load_constituencies, name='ajax_load_constituencies'),
]
