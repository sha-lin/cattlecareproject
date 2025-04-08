from django import forms
from .models import FarmerVaccination

class VaccinationForm(forms.ModelForm):
    class Meta:
        model = FarmerVaccination
        fields = ['phone', 'vaccination_date']