from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect, get_object_or_404

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
    'level_of_study',
    'school',
    'admission_number',  # Reg No/Admin No
    'amount_requested',  # Annual Fees
    'constituency',
    'family_status_display',
    'disability_display',
    'status',  # Application status
    'date_applied',  # formatted created_at
)

# Family status dynamically from obj
def family_status_display(self, obj):
    if obj.family_status:
        # Replace underscores with spaces and capitalize each word
        return obj.family_status.replace('_', ' ').title()
    return '-'
family_status_display.short_description = 'Family Status'

# Disability dynamically from obj
def disability_display(self, obj):
    if obj.disability:
        return obj.disability.capitalize()  # Yes / No
    return '-'
disability_display.short_description = 'Disability'

    list_filter = (
        'status',
        'county',
        'constituency',
        'level_of_study',
        'created_at',
    )

    search_fields = (
        'full_name',
        'id_no',
        'admission_number',
        'school',
    )

    readonly_fields = ('created_at',)

    # 🔑 MAIN FIX IS HERE
    def get_fieldsets(self, request, obj=None):

        base_fieldsets = [
            ('Student & Status', {
                'fields': ('student_user', 'status', 'created_at')
            }),

            ('Personal Information', {
                'fields': (
                    'full_name',
                    'id_no',
                    'birth_cert_no',
                    'gender',
                    'identity_document',
                    'disability',
                    'disability_type',
                    'disability_document',
                )
            }),

            ('Education Details', {
                'fields': (
                    'level_of_study',
                    'school',
                    'course',
                    'admission_number',
                    'year_of_study',
                    'performance',
                    'amount_requested',
                    'document',
                    'transcript',
                )
            }),

            ('Location', {
                'fields': (
                    'county',
                    'constituency',
                    'ward',
                    'location',
                    'sub_location',
                    'polling_station',
                )
            }),
        ]

        # If object is not yet created
        if not obj:
            base_fieldsets.append(
                ('Family Background', {
                    'fields': ('family_status',)
                })
            )
            return base_fieldsets

        family_fields = []
        status = obj.family_status

        if status == 'both_alive':
            family_fields = [
                'father_name', 'father_phone', 'father_occupation', 'father_id',
                'mother_name', 'mother_phone', 'mother_occupation', 'mother_id',
            ]

        elif status == 'mother_dead':
            family_fields = [
                'mother_name', 'mother_phone', 'mother_occupation', 'mother_id',
                'father_death_no', 'father_death_doc',
            ]

        elif status == 'father_dead':
            family_fields = [
                'father_name', 'father_phone', 'father_occupation', 'father_id',
                'mother_death_no', 'mother_death_doc',
            ]

        elif status == 'single_mother':
            family_fields = [
                'mother_name', 'mother_phone', 'mother_occupation', 'mother_id',
            ]

        elif status == 'single_father':
            family_fields = [
                'father_name', 'father_phone', 'father_occupation', 'father_id',
            ]

        elif status == 'orphan':
            family_fields = [
                'father_death_no', 'father_death_doc',
                'mother_death_no', 'mother_death_doc',
                'guardian_name', 'guardian_phone', 'guardian_occupation',
            ]

        # ✅ SHOW ONLY FILLED FIELDS
        family_fields = [
            field for field in family_fields
            if getattr(obj, field)
        ]

        if family_fields:
            base_fieldsets.append(
                ('Family Background', {
                    'fields': tuple(family_fields)
                })
            )

        base_fieldsets.append(
            ('Siblings', {
                'fields': ('siblings_names', 'siblings_amounts')
            })
        )

        base_fieldsets.append(
            ('Referees', {
                'fields': (
                    'referee1_name',
                    'referee1_phone',
                    'referee2_name',
                    'referee2_phone',
                )
            })
        )

        return base_fieldsets

    # ---------------------------
    # Display created_at as Date Applied
    # ---------------------------
    def date_applied(self, obj):
        return obj.created_at.strftime("%d %b %Y")
    date_applied.admin_order_field = 'created_at'
    date_applied.short_description = 'Date Applied'

    # ---------------------------
    # Document clickable link
    # ---------------------------
    def document_link(self, obj):
        if obj.document:
            return format_html('<a href="{}" target="_blank">View Document</a>', obj.document.url)
        return "-"
    document_link.short_description = 'Document'

    # ---------------------------
    # Approve / Reject buttons
    # ---------------------------
    def action_buttons(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a class="button" href="{}">Approve</a>&nbsp;'
                '<a class="button" href="{}">Reject</a>',
                f'approve/{obj.id}/', f'reject/{obj.id}/'
            )
        return '-'

    action_buttons.short_description = 'Actions'
    action_buttons.allow_tags = True

    # ---------------------------
    # Custom URLs for actions
    # ---------------------------
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('approve/<int:application_id>/', self.admin_site.admin_view(self.approve_app), name='approve_app'),
            path('reject/<int:application_id>/', self.admin_site.admin_view(self.reject_app), name='reject_app'),
        ]
        return custom_urls + urls

    # ---------------------------
    # Button handlers
    # ---------------------------
    def approve_app(self, request, application_id):
        app = get_object_or_404(Application, id=application_id)
        app.status = 'approved'
        app.save()
        self.message_user(request, f"Application '{app.full_name}' approved!")
        return redirect(request.META.get('HTTP_REFERER'))

    def reject_app(self, request, application_id):
        app = get_object_or_404(Application, id=application_id)
        app.status = 'rejected'
        app.save()
        self.message_user(request, f"Application '{app.full_name}' rejected!")
        return redirect(request.META.get('HTTP_REFERER'))

    # ---------------------------
    # Permissions & Queryset
    # ---------------------------
    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'constituencyofficer'):
            return qs.filter(constituency=request.user.constituencyofficer.constituency)
        return qs.none()

    # ---------------------------
    # Auto-create student login on first save
    # ---------------------------
    def save_model(self, request, obj, form, change):
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
