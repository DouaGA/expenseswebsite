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

class ClaimForm(forms.ModelForm):
    class Meta:
        from .models import Claim  # Importez votre modèle Claim ici
        model = Claim
        fields = '__all__'  # Ou spécifiez les champs souhaités

class ProfileForm(forms.ModelForm):
    class Meta:
        from .models import Profile  # Importez votre modèle Profile ici
        model = Profile
        fields = ['image', 'phone', 'address', 'municipality', 'bio']
