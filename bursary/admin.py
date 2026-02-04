from django.contrib import admin
from django.contrib.auth.models import Permission

from django.contrib.auth.models import User
from .models import (
    Application,
    County,
    Constituency,
    LevelOfStudy,
    ConstituencyAdmin
)

# =========================
# Application Admin
# =========================
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'admission_number',
        'constituency',
        'county',
        'level_of_study',
        'created_at'
    )

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if hasattr(request.user, 'constituencyadmin'):
            return qs.filter(
                constituency=request.user.constituencyadmin.constituency
            )

        return qs.none()


# =========================
# Constituency Admin Linking
# =========================
@admin.register(ConstituencyAdmin)
class ConstituencyAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'constituency')
    autocomplete_fields = ('user',)
    list_filter = ('constituency',)

    def save_model(self, request, obj, form, change):
        """
        Ensure linked user is staff
        """
        obj.user.is_staff = True
        obj.user.save()
        super().save_model(request, obj, form, change)

    # Only superuser can manage constituency admins
    def has_module_permission(self, request):
        return request.user.is_superuser


# =========================
# Other Models
# =========================
admin.site.register(County)
admin.site.register(Constituency)
admin.site.register(LevelOfStudy)
