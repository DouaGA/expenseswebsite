from django.contrib.auth import get_user_model
from django import forms
from django.core.exceptions import ValidationError
from .models import ClaimType, CodePostale, Citoyen, Agent, Claim, Municipality

User = get_user_model()

class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = ['title', 'claim_type', 'description', 'municipality', 'attachment', 'location_lat', 'location_lng']
        widgets = {
            'location_lat': forms.HiddenInput(),
            'location_lng': forms.HiddenInput(),
            'claim_type': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'claim_type': "Type de réclamation"
        }

class CitoyenRegisterForm(forms.Form):
    username = forms.CharField(max_length=150, label="Nom d'utilisateur")
    email = forms.EmailField(label="Adresse e-mail")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")
    nom = forms.CharField(max_length=80, label="Nom")
    prenom = forms.CharField(max_length=80, label="Prénom")

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password1']
        )
        citoyen = Citoyen.objects.create(
            user=user,
            nom=data['nom'],
            prenom=data['prenom']
        )
        return citoyen

class AgentRegisterForm(forms.Form):
    username = forms.CharField(max_length=150, label="Nom d'utilisateur")
    email = forms.EmailField(label="Adresse e-mail")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")
    nom = forms.CharField(max_length=80, label="Nom")
    prenom = forms.CharField(max_length=80, label="Prénom")
    cin = forms.CharField(max_length=8, label="CIN")
    code_postale = forms.ModelChoiceField(
        queryset=CodePostale.objects.all(),
        label="Code postal",
        required=False
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean_cin(self):
        cin = self.cleaned_data['cin']
        if not cin.isdigit() or len(cin) != 8:
            raise ValidationError("Le CIN doit contenir exactement 8 chiffres.")
        if Agent.objects.filter(cin=cin).exists():
            raise ValidationError("Ce numéro de CIN est déjà utilisé.")
        return cin

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password1']
        )
        agent = Agent.objects.create(
            user=user,
            nom=data['nom'],
            prenom=data['prenom'],
            cin=data['cin'],
            code_postale=data['code_postale']
        )
        return agent

# Add this to forms.py
from .models import Profile
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'phone', 'municipality']
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': 'Numéro de téléphone'}),
            'municipality': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'image': 'Photo de profil',
            'phone': 'Téléphone',
            'municipality': 'Municipalité'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })