from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Application, County, Constituency, LevelOfStudy

# ------------------------
# STUDENT SIGNUP FORM
# ------------------------
class StudentSignUpForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True)
    admission_number = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'full_name', 'admission_number', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        # Use admission_number as username
        user.username = self.cleaned_data['admission_number']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


# ------------------------
# STUDENT LOGIN FORM
# ------------------------
class StudentLoginForm(AuthenticationForm):
    username = forms.CharField(label='Admission Number')
    password = forms.CharField(widget=forms.PasswordInput)


# ------------------------
# BURSARY APPLICATION FORM
# ------------------------
class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'full_name',
            'admission_number',
            'school',
            'course',
            'year_of_study',
            'phone',
            'amount_requested',
            'county',
            'constituency',
            'level_of_study',
            'document',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Disable constituency initially
        self.fields['constituency'].queryset = Constituency.objects.none()
        self.fields['constituency'].widget.attrs.update({'disabled': True})

        # If form has county selected, populate constituencies
        if 'county' in self.data:
            try:
                county_id = int(self.data.get('county'))
                self.fields['constituency'].queryset = Constituency.objects.filter(county_id=county_id)
                self.fields['constituency'].widget.attrs.pop('disabled', None)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.county:
            self.fields['constituency'].queryset = Constituency.objects.filter(county=self.instance.county)
            self.fields['constituency'].widget.attrs.pop('disabled', None)
