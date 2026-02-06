from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from .models import (
    Application,
    County,
    Constituency,
    LevelOfStudy,
    ConstituencyOfficer
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

    list_filter = ('status', 'constituency', 'county', 'level_of_study')
    search_fields = ('full_name', 'admission_number', 'school', 'course')
    readonly_fields = ('created_at',)

    # Organize fields to match apply.html sections
    fieldsets = (
        ("Location & Level", {
            'fields': ('county', 'constituency', 'level_of_study')
        }),
        ("Personal Details", {
            'fields': (
                'full_name', 'admission_number', 'gender', 'id_no', 'birth_no',
                'id_copy', 'birth_copy', 'disability', 'disability_details', 'phone'
            )
        }),
        ("Educational Details", {
            'fields': (
                'reg_no', 'school', 'course', 'year_of_study', 'amount_requested',
                'annual_fees', 'fee_structure', 'academic_performance', 'transcript'
            )
        }),
        ("Geo Details", {
            'fields': ('polling_station', 'sub_location', 'location', 'ward')
        }),
        ("Family Details", {
            'fields': (
                'parents_status', 'parent_disabled',
                'disabled_parent_name', 'disabled_parent_phone',
                'disabled_parent_type', 'disabled_parent_doc'
            )
        }),
        ("Siblings Details", {
            'fields': (
                'siblings_highschool_names', 'siblings_highschool_amount',
                'siblings_college_names', 'siblings_college_amount',
                'siblings_university_names', 'siblings_university_amount'
            )
        }),
        ("Referees", {
            'fields': (
                'referee1_name', 'referee1_phone',
                'referee2_name', 'referee2_phone'
            )
        }),
        ("Supporting Document & Status", {
            'fields': ('document', 'status', 'student_user', 'created_at')
        }),
    )

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        if hasattr(request.user, 'constituencyofficer'):
            return qs.filter(
                constituency=request.user.constituencyofficer.constituency
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
# CONSTITUENCY OFFICER LINKING
# =========================
@admin.register(ConstituencyOfficer)
class ConstituencyOfficerAdmin(admin.ModelAdmin):
    list_display = ('user', 'constituency')
    list_filter = ('constituency',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(
                is_active=True,
                is_superuser=False,
                constituencyofficer__isnull=True
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
