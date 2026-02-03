from django.contrib import admin
from .models import Application, County, Constituency, LevelOfStudy, ConstituencyAdmin

# =========================
# Application Admin
# =========================
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'admission_number', 'constituency', 'county', 'level_of_study', 'created_at')
    list_filter = ('county', 'constituency', 'level_of_study')
    search_fields = ('full_name', 'admission_number', 'school', 'course', 'phone')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Superuser sees all applications
        if request.user.is_superuser:
            return qs
        # Constituency admin sees only applications in their constituency
        try:
            constituency_admin = ConstituencyAdmin.objects.get(user=request.user)
            return qs.filter(constituency=constituency_admin.constituency)
        except ConstituencyAdmin.DoesNotExist:
            return qs.none()  # Staff without constituency sees nothing

# =========================
# ConstituencyAdmin Admin
# =========================
class ConstituencyAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'constituency')
    search_fields = ('user__username', 'user__email', 'constituency__name')
    list_filter = ('constituency',)

    # Optional: only superuser can add/edit constituency admins
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

# =========================
# Register models
# =========================
admin.site.register(Application, ApplicationAdmin)
admin.site.register(County)
admin.site.register(Constituency)
admin.site.register(LevelOfStudy)
admin.site.register(ConstituencyAdmin, ConstituencyAdminAdmin)
