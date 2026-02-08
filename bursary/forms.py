from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Application, County, Constituency

# ------------------------
# STUDENT SIGNUP
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
        user.username = self.cleaned_data['admission_number']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

# ------------------------
# STUDENT LOGIN
# ------------------------
class StudentLoginForm(AuthenticationForm):
    username = forms.CharField(label='Admission Number')
    password = forms.CharField(widget=forms.PasswordInput)

# ------------------------
# APPLICATION FORM
# ------------------------
class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        # Save all fields except system-managed fields
        fields = '__all__'
        exclude = ['student_user', 'status', 'created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       self.fields['county'].queryset = County.objects.all()
        self.fields['county'].empty_label = "Select County"

        # Constituency: initially empty if no county selected
        self.fields['constituency'].queryset = Constituency.objects.none()
        self.fields['constituency'].empty_label = "Select Constituency"

        # Load constituencies if POST or editing
        if 'county' in self.data:
            try:
                county_id = int(self.data.get('county'))
                self.fields['constituency'].queryset = Constituency.objects.filter(county_id=county_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.county:
            self.fields['constituency'].queryset = self.instance.county.constituencies.all()