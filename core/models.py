from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Q


from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Q

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('agent', 'Agent'),
        ('citizen', 'Citizen'),
    ]
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='citizen'
    )
    cin = models.CharField(max_length=20, blank=True, null=True)
    municipality = models.ForeignKey('Municipality', on_delete=models.SET_NULL, null=True, blank=True)
    vpn_code = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return self.username

# Keep your other models (Wilaya, Municipality, etc.) the same
class Wilaya(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=2)

    def __str__(self):
        return self.name

class Municipality(models.Model):
    name = models.CharField(max_length=100)
    wilaya = models.ForeignKey(Wilaya, on_delete=models.CASCADE)
    postal_code = models.CharField(max_length=10, unique=True)  # Assure l'unicité
    
    class Meta:
        verbose_name_plural = "Municipalities"  # Corrige l'affichage dans l'admin
    
    def __str__(self):
        return f"{self.name} ({self.postal_code})"
class ClaimType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Claim(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Rejetée'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='claims'
    )
    claim_type = models.ForeignKey(ClaimType, on_delete=models.SET_NULL, null=True, blank=True)
    municipality = models.ForeignKey(
    Municipality,
    on_delete=models.CASCADE  # Déjà configuré comme CASCADE
)
    attachment = models.FileField(upload_to='claim_attachments/', blank=True, null=True)
    location_lat = models.FloatField(blank=True, null=True)
    location_lng = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics', default='default.jpg')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE  # Déjà configuré comme CASCADE
    )    
    bio = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.user.username} Profile"

class PostalCode(models.Model):
    gov = models.CharField(max_length=100, verbose_name="Gouvernorat")
    deleg = models.CharField(max_length=100, verbose_name="Délégation")
    cite = models.CharField(max_length=100, verbose_name="Cité")
    zip_code = models.CharField(max_length=10, verbose_name="Code Postal")

    def __str__(self):
        return f"{self.cite} - {self.zip_code}"

    class Meta:
        verbose_name = "Code Postal"
        verbose_name_plural = "Codes Postaux"