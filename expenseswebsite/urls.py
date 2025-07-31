from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from claims import views as claims_views
from django.conf import settings
from django.conf.urls.static import static
from authentication.views import RegisterView, authentication_redirect
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', include('claims.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('authentication/', include('authentication.urls', namespace='authentication')),    
    path('admin/', admin.site.urls),
    path('accounts/', include([
        path('login/', auth_views.LoginView.as_view(template_name='registration/login.html')), 
        path('logout/', auth_views.LogoutView.as_view()),
        path('register/', RegisterView.as_view(), name='register'),
        path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
        path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
        path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
        path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),  # Inclure les URLs d'inscription
       
    ])),
    path('api/municipality/', claims_views.municipality_lookup, name='municipality_lookup'),
    path('profile/', claims_views.agent_profile, name='agent_profile'),
    # In your main urls.py

    path('claims/', include('claims.urls', namespace='claims')),
    # other paths...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)