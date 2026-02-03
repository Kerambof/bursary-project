from django.contrib import admin
from django.contrib.auth.models import User
from django import forms
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
        # Constituency admin sees only applications for their constituency
        try:
            constituency_admin = ConstituencyAdmin.objects.get(user=request.user)
            return qs.filter(constituency=constituency_admin.constituency)
        except ConstituencyAdmin.DoesNotExist:
            return qs.none()  # Staff without a linked constituency sees nothing


# =========================
# ConstituencyAdmin Form
# =========================
class ConstituencyAdminForm(forms.ModelForm):
    class Meta:
        model = ConstituencyAdmin
        fields = ['user', 'constituency']

    def clean_user(self):
        user = self.cleaned_data['user']
        if not user.is_staff:
            raise forms.ValidationError("This user must be marked as staff.")
        return user


# =========================
# Register models in admin
# =========================

admin.site.register(Application, ApplicationAdmin)
admin.site.register(County)
admin.site.register(Constituency)
admin.site.register(LevelOfStudy)

@admin.register(ConstituencyAdmin)
class ConstituencyAdminAdmin(admin.ModelAdmin):
    form = ConstituencyAdminForm
    list_display = ('user', 'constituency')
