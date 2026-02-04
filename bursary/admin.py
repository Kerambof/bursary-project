from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from .models import (
    Application,
    County,
    Constituency,
    LevelOfStudy,
    ConstituencyAdmin
)

# =========================
# EXTEND USER ADMIN (FIX AUTOCOMPLETE)
# =========================
class UserAdmin(DefaultUserAdmin):
    search_fields = ('username', 'email', 'first_name', 'last_name')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# =========================
# APPLICATION ADMIN
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

        # Superuser sees all
        if request.user.is_superuser:
            return qs

        # Constituency admin sees only their constituency
        if hasattr(request.user, 'constituencyadmin'):
            return qs.filter(
                constituency=request.user.constituencyadmin.constituency
            )

        return qs.none()


# =========================
# CONSTITUENCY ADMIN LINKING
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

    def has_module_permission(self, request):
        # Only superusers manage constituency admins
        return request.user.is_superuser


# =========================
# OTHER MODELS
# =========================
admin.site.register(County)
admin.site.register(Constituency)
admin.site.register(LevelOfStudy)
