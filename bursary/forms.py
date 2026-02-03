from django import forms
from .models import Application, Constituency

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
        # Start with empty constituency options
        self.fields['constituency'].queryset = Constituency.objects.none()

        if 'county' in self.data:
            try:
                county_id = int(self.data.get('county'))
                self.fields['constituency'].queryset = Constituency.objects.filter(county_id=county_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.county:
            self.fields['constituency'].queryset = self.instance.county.constituencies
