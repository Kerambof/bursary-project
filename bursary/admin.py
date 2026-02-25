from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils.html import format_html
from django.urls import path
from cloudinary.utils import cloudinary_url
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
        'admission_number',
        'annual_fee_display',
        'constituency',
        'family_status_display',
        'disability_display',
        'status',
        'action_buttons',
        'date_applied',
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "amount_requested":
            formfield.label = "Annual Fee"
        return formfield

    def annual_fee_display(self, obj):
        return obj.amount_requested
    annual_fee_display.short_description = 'Annual Fee'
    annual_fee_display.admin_order_field = 'amount_requested'

    def family_status_display(self, obj):
        if obj.family_status:
            return obj.family_status.replace('_', ' ').title()
        return '-'
    family_status_display.short_description = 'Family Status'

    def disability_display(self, obj):
        if obj.disability:
            return obj.disability.capitalize()
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

    readonly_fields = (
        'created_at',
        'identity_document_link',
        'disability_document_link',
        'document_link',
        'transcript_link',
        'father_death_doc_link',
        'mother_death_doc_link',
    )

    # =========================
    # Cloudinary file links (all signed)
    # =========================
    def identity_document_link(self, obj):
        if obj.identity_document:
            url, _ = cloudinary_url(obj.identity_document.name, secure=True, signed=True)
            return format_html('<a href="{}" target="_blank">View Identity Document</a>', url)
        return "-"
    identity_document_link.short_description = 'Identity Document'

    def disability_document_link(self, obj):
        if obj.disability_document:
            url, _ = cloudinary_url(obj.disability_document.name, secure=True, signed=True)
            return format_html('<a href="{}" target="_blank">View Disability Document</a>', url)
        return "-"
    disability_document_link.short_description = 'Disability Document'

    def document_link(self, obj):
        if obj.document:
            url, _ = cloudinary_url(obj.document.name, secure=True, signed=True)
            return format_html('<a href="{}" target="_blank">View Document</a>', url)
        return "-"
    document_link.short_description = 'Document'

    def transcript_link(self, obj):
        if obj.transcript:
            url, _ = cloudinary_url(obj.transcript.name, secure=True, signed=True)
            return format_html('<a href="{}" target="_blank">View Transcript</a>', url)
        return "-"
    transcript_link.short_description = 'Transcript'

    def father_death_doc_link(self, obj):
        if obj.father_death_doc:
            url, _ = cloudinary_url(obj.father_death_doc.name, secure=True, signed=True)
            return format_html('<a href="{}" target="_blank">View Father Death Doc</a>', url)
        return "-"
    father_death_doc_link.short_description = 'Father Death Doc'

    def mother_death_doc_link(self, obj):
        if obj.mother_death_doc:
            url, _ = cloudinary_url(obj.mother_death_doc.name, secure=True, signed=True)
            return format_html('<a href="{}" target="_blank">View Mother Death Doc</a>', url)
        return "-"
    mother_death_doc_link.short_description = 'Mother Death Doc'

    # ------------------------
    # Remaining methods are unchanged
    # ------------------------
    def get_fieldsets(self, request, obj=None):
        base_fieldsets = [
            ('Student & Status', {
                'fields': ('student_user', 'status', 'created_at'),
                'classes': ('wide',)
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
                ),
                'classes': ('collapse', 'wide'),
            }),

            ('Education Details', {
                'fields': (
                    'level_of_study',
                    'school',
                    'course',
                    'admission_number',
                    'year_of_study',
                    'performance',
                    'amount_requested',  # ← remains same field
                    'document',
                    'transcript',
                ),
                'classes': ('wide',),
            }),

            ('Location', {
                'fields': (
                    'county',
                    'constituency',
                    'ward',
                    'location',
                    'sub_location',
                    'polling_station',
                ),
                'classes': ('wide',),
            }),
        ]

        if not obj:
            base_fieldsets.append(
                ('Family Background', {
                    'fields': ('family_status',),
                    'classes': ('wide',),
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

        base_fieldsets.append(
        ('Family Background', {
            'fields': tuple(family_fields),
            'classes': ('wide',),
        })
    )

        base_fieldsets.append(
            ('Siblings', {
                'fields': ('siblings_names', 'siblings_amounts'),
                'classes': ('wide',),
            })
        )

        base_fieldsets.append(
            ('Referees', {
                'fields': (
                    'referee1_name',
                    'referee1_phone',
                    'referee2_name',
                    'referee2_phone',
                ),
                'classes': ('wide',),
            })
        )

        # Inject Cloudinary file links into appropriate sections
        if obj:
            # Personal Information
            personal = dict(base_fieldsets[1][1])
            personal_fields = list(personal['fields'])
            if 'identity_document' in personal_fields:
                personal_fields.append('identity_document_link')
            if 'disability_document' in personal_fields:
                personal_fields.append('disability_document_link')
            personal['fields'] = tuple(personal_fields)
            base_fieldsets[1] = (base_fieldsets[1][0], personal)

            # Education Details
            education = dict(base_fieldsets[2][1])
            education_fields = list(education['fields'])
            if 'document' in education_fields:
                education_fields.append('document_link')
            if 'transcript' in education_fields:
                education_fields.append('transcript_link')
            education['fields'] = tuple(education_fields)
            base_fieldsets[2] = (base_fieldsets[2][0], education)

            # Family Background
            family = dict(base_fieldsets[3][1])
            family_fields = list(family['fields'])
            if 'father_death_doc' in family_fields:
                family_fields.append('father_death_doc_link')
            if 'mother_death_doc' in family_fields:
                family_fields.append('mother_death_doc_link')
            family['fields'] = tuple(family_fields)
            base_fieldsets[3] = (base_fieldsets[3][0], family)

        return base_fieldsets

    def date_applied(self, obj):
        return obj.created_at.strftime("%d %b %Y")
    date_applied.admin_order_field = 'created_at'
    date_applied.short_description = 'Date Applied'

    def action_buttons(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a class="button" style="background-color:#4CAF50;color:white;padding:3px 8px;border-radius:4px;text-decoration:none;" href="{}">Approve</a>&nbsp;'
                '<a class="button" style="background-color:#e74c3c;color:white;padding:3px 8px;border-radius:4px;text-decoration:none;" href="{}">Reject</a>',
                f'approve/{obj.id}/', f'reject/{obj.id}/'
            )
        return '-'

    action_buttons.short_description = 'Actions'
    action_buttons.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('approve/<int:application_id>/', self.admin_site.admin_view(self.approve_app), name='approve_app'),
            path('reject/<int:application_id>/', self.admin_site.admin_view(self.reject_app), name='reject_app'),
        ]
        return custom_urls + urls

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

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'constituencyofficer'):
            return qs.filter(constituency=request.user.constituencyofficer.constituency)
        return qs.none()

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


admin.site.register(County)
admin.site.register(Constituency)
admin.site.register(LevelOfStudy)