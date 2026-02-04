from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Application, Constituency

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
# Student Signup Form
# =========================
class StudentSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, label="Full Name")
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password1', 'password2')

# =========================
# Student Login Form
# =========================
class StudentLoginForm(AuthenticationForm):
    username = forms.CharField(label="Admission Number")
    password = forms.CharField(widget=forms.PasswordInput)
