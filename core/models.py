from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import AbstractUser, Group, Permission

from django.contrib.auth.models import User
class Wilaya(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=2)

    def __str__(self):
        return self.name

class Municipality(models.Model):
    name = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return f"{self.name} ({self.postal_code})"

class ClaimType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Claim(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (PENDING, 'En attente'),
        (ACCEPTED, 'Acceptée'),
        (REJECTED, 'Rejetée'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claims')
    municipality = models.ForeignKey(Municipality, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location_lat = models.FloatField()
    location_lng = models.FloatField()
    attachment = models.FileField(upload_to='claims/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

class CodePostale(models.Model):
    gov = models.CharField(max_length=100, verbose_name="Gouvernorat")
    deleg = models.CharField(max_length=100, verbose_name="Délégation")
    cite = models.CharField(max_length=100, verbose_name="Cité")
    zip_code = models.CharField(max_length=10, verbose_name="Code Postal")

    def __str__(self):
        return f"{self.cite} - {self.zip_code}"

    class Meta:
        verbose_name = "Code Postal"
        verbose_name_plural = "Codes Postaux"

class Citoyen(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=80)
    prenom = models.CharField(max_length=80)

    def __str__(self):
        return f"{self.nom} {self.prenom}"

    @classmethod
    def create_or_update(cls, user, nom, prenom):
        citoyen, created = cls.objects.update_or_create(
            user=user,
            defaults={'nom': nom, 'prenom': prenom}
        )
        return citoyen

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=110)
    prenom = models.CharField(max_length=110)
    cin = models.CharField(max_length=8, unique=True)
    code_postale = models.ForeignKey(CodePostale, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.cin}"



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images/', default='profile_images/default.jpg')
    phone = models.CharField(max_length=20, blank=True, null=True)
    municipality = models.ForeignKey(Municipality, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"



from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()