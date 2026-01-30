from django.urls import path
from .views import apply, success

urlpatterns = [
    path('', apply, name='apply'),
    path('success/', success, name='success'),
]
