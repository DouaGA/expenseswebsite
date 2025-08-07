from django.urls import path
from . import views
from core.views import get_cites

app_name = 'core'

urlpatterns = [
    # Pages principales
    path('', views.home, name='home'),
    path('access-denied/', views.access_denied, name='access_denied'),
    path('login/', views.login_selector, name='login_selector'),

    # Authentification
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('agent/login/', views.AgentLoginView.as_view(), name='agent_login'),
    path('citizen/login/', views.CitizenLoginView.as_view(), name='citizen_login'),
    path('register/agent/', views.AgentRegisterView.as_view(), name='agent_register'),
    path('register/citizen/', views.CitizenRegisterView.as_view(), name='citizen_register'),
    path('api/get_cites/', get_cites, name='get_cites'),

    # Tableaux de bord Agent
    path('agent/dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('citizen/claims/', views.claims_list, name='claims_list'),
    path('citizen/claims/create/', views.create_claim, name='create_claim'),
    path('agent/claims/<int:pk>/', views.claim_detail, name='claim_detail'),
    path('citizen/claims/<int:pk>/update/<str:status>/', views.update_claim_status, name='update_claim_status'),
    path('agent/map/', views.claims_map, name='claims_map'),
    path('agent/stats/', views.stats_view, name='stats'),
    path('agent/export/', views.export_claims, name='export_claims'),

    # Tableau de bord Citoyen
    path('citizen/dashboard/', views.citizen_dashboard, name='citizen_dashboard'),
    path('profile/', views.profile_view, name='profile'),

    # Administration
    path('staff/login/', views.StaffLoginView.as_view(), name='staff_login'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    
    # Profil
    path('profile/agent_profile', views.profile_view, name='agent_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
]