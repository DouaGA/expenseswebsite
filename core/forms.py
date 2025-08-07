# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class AgentRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'cin']
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

class CitizenRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']  # Modifiez selon vos besoins

from .models import Claim, Municipality, ClaimType

class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim  # Remplacez par votre modèle Claim
        fields = ['title', 'claim_type', 'municipality', 'description', 'attachment', 'location_lat', 'location_lng']
        widgets = {
            'location_lat': forms.HiddenInput(),
            'location_lng': forms.HiddenInput(),
            'municipality': forms.Select(attrs={'class': 'form-control'}),

        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['municipality'].queryset = Municipality.objects.all()
        self.fields['claim_type'].queryset = ClaimType.objects.all()
class ProfileForm(forms.ModelForm):
    class Meta:
        from .models import Profile  # Importez votre modèle Profile ici
        model = Profile
        fields = ['image', 'phone', 'address', 'municipality', 'bio']
