from django.core.management.base import BaseCommand
from core.models import PostalCode, Municipality, Wilaya

class Command(BaseCommand):
    help = 'Importe les codes postaux dans le modèle Municipality'

    def handle(self, *args, **options):
        # 1. Créer une wilaya par défaut si elle n'existe pas
        wilaya, created = Wilaya.objects.get_or_create(
            name="Alger",
            defaults={'code': "16"}
        )
        
        # 2. Importer les données
        count = 0
        for pc in PostalCode.objects.all():
            # Nettoyer le nom de la municipalité
            mun_name = ' '.join(pc.cite.split('-')[0].strip().split())
            
            # Créer la municipalité si elle n'existe pas
            _, created = Municipality.objects.get_or_create(
                name=mun_name,
                postal_code=pc.zip_code,
                defaults={'wilaya': wilaya}
            )
            
            if created:
                count += 1
                self.stdout.write(f"Ajouté : {mun_name} ({pc.zip_code})")
        
        self.stdout.write(self.style.SUCCESS(f'Importation terminée. {count} nouvelles municipalités créées.'))