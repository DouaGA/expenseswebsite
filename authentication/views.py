from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from .models import UserProfile  # Relative import since models.py is in the same appfrom .utils import account_activation_token
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login  # Ajoutez cette ligne
from django.contrib.auth.models import User
from django.contrib import messages

class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        try:
            validate_email(email)
            if User.objects.filter(email=email).exists():
                return JsonResponse({'email_error': 'Email déjà utilisé'}, status=409)
            return JsonResponse({'email_valid': True})
        except ValidationError:
            return JsonResponse({'email_error': 'Email invalide'}, status=400)

class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Le nom d\'utilisateur ne doit contenir que des caractères alphanumériques'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'Nom d\'utilisateur déjà utilisé'}, status=409)
        return JsonResponse({'username_valid': True})


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('claims:claims_dashboard')
        return render(request, 'authentication/register.html')

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not all([username, email, password, password2]):
            messages.error(request, "Tous les champs sont obligatoires")
            return render(request, 'authentication/register.html')

        if password != password2:
            messages.error(request, "Les mots de passe ne correspondent pas")
            return render(request, 'authentication/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris")
            return render(request, 'authentication/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé")
            return render(request, 'authentication/register.html')

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Inscription réussie ! Bienvenue.")
            return redirect('claims:claims_dashboard')
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la création du compte: {str(e)}")
            return render(request, 'authentication/register.html')

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('claims:claims_dashboard')
        return render(request, 'authentication/login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('claims:claims_dashboard')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
            return render(request, 'authentication/login.html')


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if user.is_active:
                messages.info(request, 'Compte déjà activé')
                return redirect('login')
            
            if not account_activation_token.check_token(user, token): # type: ignore
                messages.error(request, 'Lien d\'activation invalide ou expiré')
                return redirect('login')
            
            user.is_active = True
            user.save()
            messages.success(request, 'Compte activé avec succès')
            return redirect('login')

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, 'Lien d\'activation invalide')
            return redirect('login')


class LogoutView(View):
    @method_decorator(login_required)
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'Vous avez été déconnecté')
        return redirect('authentication:login')

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
from django.shortcuts import redirect

def authentication_redirect(request):
    return redirect('authentication:login')  # Avec namespace

