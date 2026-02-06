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
        # Set username to admission_number
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
            # Location & Level
            'county', 'constituency', 'level_of_study',
            # Personal Details
            'full_name', 'admission_number', 'gender', 'id_no', 'birth_no',
            'id_copy', 'birth_copy', 'disability', 'disability_details', 'phone',
            # Educational Details
            'reg_no', 'school', 'course', 'year_of_study', 'amount_requested',
            'annual_fees', 'fee_structure', 'academic_performance', 'transcript',
            # Geo Details
            'polling_station', 'sub_location', 'location', 'ward',
            # Family Details
            'parents_status', 'parent_disabled', 'disabled_parent_name', 'disabled_parent_phone',
            'disabled_parent_type', 'disabled_parent_doc',
            # Siblings
            'siblings_highschool_names', 'siblings_highschool_amount',
            'siblings_college_names', 'siblings_college_amount',
            'siblings_university_names', 'siblings_university_amount',
            # Referees
            'referee1_name', 'referee1_phone', 'referee2_name', 'referee2_phone',
            # Supporting Document
            'document',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initially, no constituencies are loaded
        self.fields['constituency'].queryset = Constituency.objects.none()
        self.fields['constituency'].widget.attrs.update({'disabled': True})

        if 'county' in self.data:
            try:
                county_id = int(self.data.get('county'))
                self.fields['constituency'].queryset = Constituency.objects.filter(county_id=county_id)
                self.fields['constituency'].widget.attrs.pop('disabled', None)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.county:
            self.fields['constituency'].queryset = self.instance.county.constituencies.all()
            self.fields['constituency'].widget.attrs.pop('disabled', None)
