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
    # Cloudinary file links (FIXED)
    # =========================
    def identity_document_link(self, obj):
        if obj.identity_document:
            return format_html(
                '<a href="{}" target="_blank">View Identity Document</a>',
                obj.identity_document.url
            )
        return "-"
    identity_document_link.short_description = 'Identity Document'

    def disability_document_link(self, obj):
        if obj.disability_document:
            return format_html(
                '<a href="{}" target="_blank">View Disability Document</a>',
                obj.disability_document.url
            )
        return "-"
    disability_document_link.short_description = 'Disability Document'

    def document_link(self, obj):
        if obj.document:
            return format_html(
                '<a href="{}" target="_blank">View Document</a>',
                obj.document.url
            )
        return "-"
    document_link.short_description = 'Document'

    def transcript_link(self, obj):
        if obj.transcript:
            return format_html(
                '<a href="{}" target="_blank">View Transcript</a>',
                obj.transcript.url
            )
        return "-"
    transcript_link.short_description = 'Transcript'

    def father_death_doc_link(self, obj):
        if obj.father_death_doc:
            return format_html(
                '<a href="{}" target="_blank">View Father Death Doc</a>',
                obj.father_death_doc.url
            )
        return "-"
    father_death_doc_link.short_description = 'Father Death Doc'

    def mother_death_doc_link(self, obj):
        if obj.mother_death_doc:
            return format_html(
                '<a href="{}" target="_blank">View Mother Death Doc</a>',
                obj.mother_death_doc.url
            )
        return "-"
    mother_death_doc_link.short_description = 'Mother Death Doc'

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