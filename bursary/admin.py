from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Application, County, Constituency, LevelOfStudy, ConstituencyAdmin

# =========================
# Application Admin
# =========================

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'admission_number', 'constituency', 'county', 'level_of_study', 'created_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            constituency_admin = ConstituencyAdmin.objects.get(user=request.user)
            return qs.filter(constituency=constituency_admin.constituency)
        except ConstituencyAdmin.DoesNotExist:
            return qs.none()  # Staff without constituency sees nothing

# =========================
# ConstituencyAdmin Inline
# =========================

class ConstituencyAdminInline(admin.StackedInline):
    model = ConstituencyAdmin
    can_delete = False
    verbose_name_plural = 'Constituency Admin'


# =========================
# User Admin Override
# =========================

class UserAdmin(BaseUserAdmin):
    inlines = (ConstituencyAdminInline,)

# Unregister original User admin and register new one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# =========================
# Register models
# =========================

admin.site.register(Application, ApplicationAdmin)
admin.site.register(County)
admin.site.register(Constituency)
admin.site.register(LevelOfStudy)
