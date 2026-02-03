from django import forms
from django.contrib.auth.models import User
from .models import Application, Constituency, ConstituencyAdmin

# =========================
# Application Form
# =========================

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'full_name', 'admission_number', 'school', 'course',
            'year_of_study', 'phone', 'amount_requested',
            'county', 'constituency', 'level_of_study', 'document'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['constituency'].queryset = Constituency.objects.none()

        if 'county' in self.data:
            try:
                county_id = int(self.data.get('county'))
                self.fields['constituency'].queryset = Constituency.objects.filter(county_id=county_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.county:
            self.fields['constituency'].queryset = self.instance.county.constituencies


# =========================
# Constituency Admin Creation Form (for superusers)
# =========================

class ConstituencyAdminCreationForm(forms.ModelForm):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = ConstituencyAdmin
        fields = ['constituency', 'user']

    def save(self, commit=True):
        # Create user first
        username = self.cleaned_data['user'].username
        password = self.cleaned_data['password']
        email = self.cleaned_data['email']
        full_name = self.cleaned_data['full_name']

        user = self.cleaned_data['user']
        user.set_password(password)
        user.email = email
        user.first_name = full_name
        user.is_staff = True
        if commit:
            user.save()
        
        admin_instance = super().save(commit=False)
        admin_instance.user = user
        if commit:
            admin_instance.save()
        return admin_instance
