from django.urls import path
from .views import apply, success, load_constituencies

urlpatterns = [
    path('', apply, name='apply'),
    path('success/', success, name='success'),
    path('ajax/load-constituencies/', load_constituencies, name='ajax_load_constituencies'),
]
