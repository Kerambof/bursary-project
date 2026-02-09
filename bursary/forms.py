from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Application, County, Constituency

# ------------------------
# STUDENT SIGNUP
# ------------------------
class StudentSignUpForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True)
    id_no = forms.CharField(max_length=20, required=True, label="ID No / Birth Certificate No")
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ('full_name', 'id_no', 'email', 'password1', 'password2')

    def clean_id_no(self):
        id_no = self.cleaned_data['id_no']
        if User.objects.filter(username=id_no).exists():
            raise forms.ValidationError("This ID / Birth Certificate No is already registered.")
        return id_no

    def save(self, commit=True):
        user = super().save(commit=False)
        # Use ID No / Birth Certificate No as username
        user.username = self.cleaned_data['id_no']

        # Store full name in first_name and last_name
        full_name = self.cleaned_data['full_name'].strip()
        parts = full_name.split(" ", 1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ""

        # Store email if provided
        user.email = self.cleaned_data.get('email', '')

        if commit:
            user.save()
        return user

# ------------------------
# STUDENT LOGIN
# ------------------------
class StudentLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='ID No / Birth Certificate No',
        widget=forms.TextInput(attrs={'placeholder': 'Enter your ID/Birth Cert No'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

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
