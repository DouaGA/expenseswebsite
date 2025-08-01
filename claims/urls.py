from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # Page d'accueil
    path('', views.home, name='home'),
    
    # Tableau de bord
    path('dashboard/', login_required(views.dashboard), name='claims_dashboard'),
    
    # Fonctionnalités principales
    path('map/', views.claim_map, name='claims_map'),
    path('stats/', views.claim_stats, name='claims_stats'),
    
    # Gestion de profil
    path('profile/', views.agent_profile, name='agent_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Export de données
    path('export/', views.export_claims, name='export_claims'),
    
    # API Endpoints
    path('api/claims/', views.api_claims, name='api_claims'),
    path('api/claims/<int:claim_id>/', views.api_claim_details, name='api_claim_details'),
    path('api/claims/update-status/<int:claim_id>/<str:status>/', 
         views.update_claim_status, 
         name='update_claim_status'),
    
    # Gestion des réclamations
    path('claims/<int:claim_id>/', views.claim_detail, name='claim_detail'),
    
    # Gestion des mots de passe
    path('password-change/', 
         auth_views.PasswordChangeView.as_view(
             template_name='password_change.html'
         ), 
         name='password_change'),
    path('password-change/done/', 
         auth_views.PasswordChangeDoneView.as_view(
             template_name='password_change_done.html'
         ), 
         name='password_change_done'),
]