from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import (
     get_cites, home,
    citizen_dashboard, agent_dashboard,
    create_claim
)
from django.contrib.auth.views import LogoutView
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.home, name='home'),
    path('login_agent/', views.login_agent, name='login_agent'),
    path('login_citoyen/', views.login_citoyen, name='login_citoyen'),
    path('signup_citoyen/', views.signup_citoyen, name='signup_citoyen'),
    path('signup_agent/', views.signup_agent, name='signup_agent'),
    
    path('logout/', LogoutView.as_view(), name='logout'),
    path('citizen/dashboard/', views.citizen_dashboard, name='citizen_dashboard'),
    path('agent/dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('citizen/claims/create/', create_claim, name='create_claim'),
    path('api/get_cites/', get_cites, name='get_cites'),
    
    path('agent/claims/', views.claims_list, name='claims_list'),
    path('agent/claims/<int:pk>/', views.agent_claim_detail, name='agent_claim_detail'),
    path('agent/claims/<int:pk>/update/<str:status>/', views.update_claim_status, name='update_claim_status'),
    path('agent/map/', views.claims_map, name='claims_map'),
    path('agent/stats/', views.stats_view, name='stats'),
    path('agent/export/', views.export_claims, name='export_claims'),
    
    path('citizen/claims/', views.claims_list, name='claims_list'),
    path('citizen/claims/<int:pk>/', views.citizen_claim_detail, name='citizen_claim_detail'),
    path('citizen/claims/<int:pk>/edit/', views.edit_claim, name='edit_claim'),
    path('citizen/claims/<int:pk>/delete/', views.delete_claim, name='delete_claim'),
    path('api/claims/', views.api_claims, name='api_claims'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)