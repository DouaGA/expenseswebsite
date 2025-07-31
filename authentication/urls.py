from django.urls import path
from django.views.generic import RedirectView
from .views import (EmailValidationView, UsernameValidationView, 
                    RegisterView, VerificationView, 
                    LoginView, LogoutView, CustomLoginView, )

app_name = 'authentication'  # Add this line

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('', RedirectView.as_view(),name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    path('activate/<uidb64>/<token>/', VerificationView.as_view(), name='activate'),
    path('validate-email/', EmailValidationView.as_view(), name='validate_email'),
    path('validate-username/', UsernameValidationView.as_view(), name='validate_username'),
]