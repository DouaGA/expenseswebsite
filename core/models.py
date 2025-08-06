from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import User

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('citizen', 'Citizen'),
        ('agent', 'Agent'),
        ('Staff', 'Staff Admin')
    ]
    
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES, 
        default='citizen'
    )
    cin = models.CharField(max_length=255, unique=False, blank=True, null=True)    
    municipality = models.ForeignKey(
        'Municipality', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    vpn_code = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    class Meta:
      db_table = 'core_user'  # Explicitement définir le nom de table
      constraints = [
            models.UniqueConstraint(fields=['cin'], name='unique_cin'),
            models.UniqueConstraint(fields=['email'], name='unique_email'),
        ]

    def clean(self):
        if self.user_type == 'agent' and not self.municipality:
            raise ValidationError("Agents must have an assigned municipality.")
        if self.user_type == 'agent' and not self.vpn_code:
            raise ValidationError("Agents must have a VPN code.")

class Wilaya(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=2)

    def __str__(self):
        return self.name

class Municipality(models.Model):
    name = models.CharField(max_length=100)
    wilaya = models.ForeignKey(Wilaya, on_delete=models.CASCADE)
    postal_code = models.CharField(max_length=10)
    
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
    claim_type = models.ForeignKey(
        ClaimType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics', default='default.jpg')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    municipality = models.ForeignKey(Municipality, on_delete=models.SET_NULL, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} Profile"