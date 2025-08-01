from django.contrib import admin
from .models import Claim, ClaimType, Municipality, Profile
from django.utils.html import format_html

class ClaimAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'get_claim_type', 'status', 'created_at', 'get_created_by', 'location_link')
    list_filter = ('status', 'claim_type', 'created_at')
    search_fields = ('title', 'description')
    list_per_page = 20
    readonly_fields = ('location_link', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'claim_type', 'status')
        }),
        ('Localisation', {
            'fields': ('location_lat', 'location_lng', 'municipality', 'location_link')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_claim_type(self, obj):
        return obj.claim_type.name if obj.claim_type else "N/A"
    get_claim_type.short_description = 'Type'

    def get_created_by(self, obj):
        return obj.created_by.username if obj.created_by else "N/A"
    get_created_by.short_description = 'Créé par'
    
    def location_link(self, obj):
        if obj.location_lat and obj.location_lng:
            return format_html(
                '<a href="https://www.google.com/maps?q={},{}" target="_blank">Voir sur la carte</a>',
                obj.location_lat,
                obj.location_lng
            )
        return "Non spécifié"
    location_link.short_description = 'Lien carte'

# Supprimez cette ligne si elle existe ailleurs dans le fichier
# admin.site.register(Claim, ClaimAdmin)


class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ('name', 'wilaya', 'postal_code', 'code')
    search_fields = ('name', 'wilaya', 'postal_code')

admin.site.register(Municipality, MunicipalityAdmin)
admin.site.register(Claim, ClaimAdmin)
admin.site.register(ClaimType)
admin.site.register(Profile)