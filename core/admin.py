from django.contrib import admin
from .models import Citoyen, Agent, CodePostale, Claim, ClaimType, Municipality

admin.site.register(Citoyen)
admin.site.register(Agent)
admin.site.register(Claim)
admin.site.register(ClaimType)
admin.site.register(Municipality)
admin.site.register(CodePostale)