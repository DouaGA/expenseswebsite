from django.urls import path
from django.contrib.auth import views as auth_views
from .views import EmailValidationView, UsernameValidationView, RegistrationView, VerificationView, LoginView, LogoutView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('activate/<uidb64>/<token>/', VerificationView.as_view(), name='activate'),
    path('validate-email/', EmailValidationView.as_view(), name='validate_email'),
    path('validate-username/', UsernameValidationView.as_view(), name='validate_username'),
    
    # Ajoutez ces URLs pour la réinitialisation de mot de passe
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='authentication/password_reset.html',
             email_template_name='authentication/password_reset_email.html',
             subject_template_name='authentication/password_reset_subject.txt'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='authentication/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='authentication/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='authentication/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]