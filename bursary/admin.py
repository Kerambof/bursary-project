from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from .models import (
    Application,
    County,
    Constituency,
    LevelOfStudy,
    ConstituencyAdmin
)


# =========================
# APPLICATION ADMIN
# =========================
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):

    list_display = (
        'full_name',
        'admission_number',
        'constituency',
        'status',
        'created_at'
    )

    list_filter = ('status', 'constituency')
    search_fields = ('full_name', 'admission_number')
    readonly_fields = ('created_at',)

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

    def save_model(self, request, obj, form, change):
        """
        Auto-create student login on first save
        """
        if not obj.student_user:
            user = User.objects.create(
                username=obj.admission_number,
                password=make_password(obj.admission_number),
                is_active=True
            )
            obj.student_user = user

        super().save_model(request, obj, form, change)


# =========================
# CONSTITUENCY ADMIN LINKING
# =========================
@admin.register(ConstituencyAdmin)
class ConstituencyAdminAdmin(admin.ModelAdmin):

    list_display = ('user', 'constituency')
    list_filter = ('constituency',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(
                is_active=True,
                is_superuser=False,
                constituencyadmin__isnull=True
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.user.is_staff = True
        obj.user.save()
        super().save_model(request, obj, form, change)

    def has_module_permission(self, request):
        return request.user.is_superuser


# =========================
# OTHER MODELS
# =========================
admin.site.register(County)
admin.site.register(Constituency)
admin.site.register(LevelOfStudy)
