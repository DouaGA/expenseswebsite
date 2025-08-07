from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Claim, Municipality, ClaimType, Profile
from core.models import PostalCode

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'municipality')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('user_type', 'cin', 'municipality', 'vpn_code')}),
    )

admin.site.register(PostalCode)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Claim)
admin.site.register(Municipality)
admin.site.register(ClaimType)
admin.site.register(Profile)