from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import update_claim_status
from django.views.generic import RedirectView


urlpatterns = [
    path('', views.dashboard, name='claims_dashboard'),
    path('', RedirectView.as_view(url='claims/'), name='home'),  # Add this line

    path('map/', views.claim_map, name='claims_map'),  # Modifié
    path('stats/', views.claim_stats, name='claims_stats'),
    path('profile/', views.agent_profile, name='agent_profile'),
    path('export/', views.export_claims, name='export_claims'),
    path('api/claims/<int:claim_id>/', views.api_claim_details, name='api_claim_details'),
    path('api/claims/update-status/<int:claim_id>/<str:status>/', 
         views.update_claim_status, 
         name='update_claim_status'),
    path('api/claims/', views.api_claims, name='api_claims'),  # Modifié
    path('profile/edit/', views.edit_profile, name='edit_profile'),
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
    path('<int:pk>/', views.claim_detail, name='claim_detail'),  
    path('claims/<int:claim_id>/', views.claim_detail, name='claim_detail'),

]