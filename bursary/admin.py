from django.contrib import admin
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
            return qs.none()


# =========================
# ConstituencyAdmin Admin
# =========================

class ConstituencyAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'constituency')
    # Only superusers can manage constituency admins
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.none()


# =========================
# Register models
# =========================

admin.site.register(Application, ApplicationAdmin)
admin.site.register(County)
admin.site.register(Constituency)
admin.site.register(LevelOfStudy)
admin.site.register(ConstituencyAdmin, ConstituencyAdminAdmin)
