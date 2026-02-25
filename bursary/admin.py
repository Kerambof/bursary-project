from django.contrib import admin
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.urls import path
from django.utils.html import format_html

from cloudinary.utils import cloudinary_url

from .models import (
    Application,
    Constituency,
    ConstituencyOfficer,
    County,
    LevelOfStudy,
)

# =====================================================
# APPLICATION ADMIN
# =====================================================

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """Admin configuration for `Application` entries.

    This class only styles the admin interface (list display, filters,
    read-only links, and custom field labels). It does not alter any
    business logic.
    """

    list_display = (
        "full_name",
        "level_of_study",
        "school",
        "admission_number",
        "annual_fee_display",
        "constituency",
        "family_status_display",
        "disability_display",
        "status",
        "action_buttons",
        "date_applied",
    )

    list_filter = (
        "status",
        "county",
        "constituency",
        "level_of_study",
        "created_at",
    )

    search_fields = (
        "full_name",
        "id_no",
        "admission_number",
        "school",
    )

    readonly_fields = (
        "created_at",
        "identity_document_link",
        "disability_document_link",
        "document_link",
        "transcript_link",
        "father_death_doc_link",
        "mother_death_doc_link",
    )

    # Rename amount_requested label in the form
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "amount_requested":
            formfield.label = "Annual Fee"
        return formfield

    # ---------- list column helpers ----------
    def annual_fee_display(self, obj):
        return obj.amount_requested

    annual_fee_display.short_description = "Annual Fee"
    annual_fee_display.admin_order_field = "amount_requested"

    def family_status_display(self, obj):
        return obj.family_status.replace("_", " ").title() if obj.family_status else "-"

    family_status_display.short_description = "Family Status"

    def disability_display(self, obj):
        return obj.disability.capitalize() if obj.disability else "-"

    disability_display.short_description = "Disability"

    def date_applied(self, obj):
        return obj.created_at.strftime("%d %b %Y")

    date_applied.short_description = "Date Applied"
    date_applied.admin_order_field = "created_at"

    # ---------- Cloudinary signed links ----------
    def generate_link(self, file_field, text):
        """Return a signed Cloudinary link (if file exists) or '-' otherwise."""
        if file_field:
            url, _ = cloudinary_url(file_field.name, secure=True, signed=True)
            return format_html("<a href=\"{}\" target=\"_blank\">{}</a>", url, text)
        return "-"

    def identity_document_link(self, obj):
        return self.generate_link(obj.identity_document, "View Identity Document")

    def disability_document_link(self, obj):
        return self.generate_link(obj.disability_document, "View Disability Document")

    def document_link(self, obj):
        return self.generate_link(obj.document, "View Document")

    def transcript_link(self, obj):
        return self.generate_link(obj.transcript, "View Transcript")

    def father_death_doc_link(self, obj):
        return self.generate_link(obj.father_death_doc, "View Father Death Doc")

    def mother_death_doc_link(self, obj):
        return self.generate_link(obj.mother_death_doc, "View Mother Death Doc")

    # ---------- customized fieldsets ----------
    def get_fieldsets(self, request, obj=None):
        return [
            ("Student & Status", {"fields": ("student_user", "status", "created_at")}),
            (
                "Personal Information",
                {
                    "fields": (
                        "full_name",
                        "id_no",
                        "birth_cert_no",
                        "gender",
                        "identity_document",
                        "identity_document_link",
                        "disability",
                        "disability_type",
                        "disability_document",
                        "disability_document_link",
                    )
                },
            ),
            (
                "Education Details",
                {
                    "fields": (
                        "level_of_study",
                        "school",
                        "course",
                        "admission_number",
                        "year_of_study",
                        "performance",
                        "amount_requested",
                        "document",
                        "document_link",
                        "transcript",
                        "transcript_link",
                    )
                },
            ),
            (
                "Location",
                {
                    "fields": (
                        "county",
                        "constituency",
                        "ward",
                        "location",
                        "sub_location",
                        "polling_station",
                    )
                },
            ),
        ]

    # ---------- action buttons in list view ----------
    def action_buttons(self, obj):
        if obj.status == "pending":
            approve_url = f"approve/{obj.id}/"
            reject_url = f"reject/{obj.id}/"
            approve_btn = (
                '<a class="button" '
                'style="background:#4CAF50;color:white;padding:3px 8px;border-radius:4px;text-decoration:none;" '
                f'href="{approve_url}">Approve</a>'
            )
            reject_btn = (
                '<a class="button" '
                'style="background:#e74c3c;color:white;padding:3px 8px;border-radius:4px;text-decoration:none;" '
                f'href="{reject_url}">Reject</a>'
            )
            return format_html("{}&nbsp;{}", approve_btn, reject_btn)
        return "-"

    action_buttons.short_description = "Actions"

    # ---------- custom admin URLs ----------
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "approve/<int:application_id>/",
                self.admin_site.admin_view(self.approve_app),
                name="approve_app",
            ),
            path(
                "reject/<int:application_id>/",
                self.admin_site.admin_view(self.reject_app),
                name="reject_app",
            ),
        ]
        return custom_urls + urls

    def approve_app(self, request, application_id):
        app = get_object_or_404(Application, id=application_id)
        app.status = "approved"
        app.save()
        self.message_user(request, f"Application '{app.full_name}' approved!")
        return redirect(request.META.get("HTTP_REFERER"))

    def reject_app(self, request, application_id):
        app = get_object_or_404(Application, id=application_id)
        app.status = "rejected"
        app.save()
        self.message_user(request, f"Application '{app.full_name}' rejected!")
        return redirect(request.META.get("HTTP_REFERER"))

    # ---------- permissions & queryset filtering ----------
    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, "constituencyofficer"):
            return qs.filter(constituency=request.user.constituencyofficer.constituency)
        return qs.none()

    # ---------- auto-create student user when saving ----------
    def save_model(self, request, obj, form, change):
        if not obj.student_user:
            user = User.objects.create(
                username=obj.admission_number,
                password=make_password(obj.admission_number),
                is_active=True,
            )
            obj.student_user = user

        super().save_model(request, obj, form, change)


# =====================================================
# CONSTITUENCY OFFICER ADMIN
# =====================================================

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


# =====================================================
# REGISTER OTHER MODELS
# =====================================================

admin.site.register(County)
admin.site.register(Constituency)
admin.site.register(LevelOfStudy)