from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentification (gérée par l'app authentication)
    path('auth/', include('authentication.urls')),
    
    # Application principale (claims)
    path('', include('claims.urls')),
    
    # Redirection par défaut
    path('', RedirectView.as_view(pattern_name='home', permanent=False)),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)