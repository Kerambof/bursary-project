from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('grappelli/', include('grappelli.urls')),  # Grappelli admin
    path('admin/', admin.site.urls),                # Default Django admin
    path('', include('bursary.urls')),             # Bursary app routes
]
