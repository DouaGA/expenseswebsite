from django.core.management.base import BaseCommand
from core.models import CodePostale, Municipality, Wilaya
import json
from pathlib import Path

class Command(BaseCommand):
    help = 'Importe les codes postaux et municipalités'

    def handle(self, *args, **options):
        json_path = Path('core/templates/core/data/zip-postcodes.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                postal_data = json.load(f)
                
            created_count = 0
            updated_count = 0
            
            for item in postal_data:
                # Nettoyage des données
                gov_name = item['Gov'].strip()
                deleg_name = item['Deleg'].strip()
                cite_name = item['Cite'].strip()
                zip_code = item['zip'].strip()
                mun_name = ' '.join(cite_name.split('-')[0].strip().split())
                
                # Gestion de la Wilaya
                wilaya, _ = Wilaya.objects.get_or_create(
                    name=gov_name,
                    defaults={'code': zip_code[:2]}
                )
                
                # Gestion de la Municipalité
                mun, created = Municipality.objects.update_or_create(
                    postal_code=zip_code,
                    defaults={
                        'name': mun_name,
                        'wilaya': wilaya,
                        'delegation': deleg_name
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f"+ {mun_name} ({zip_code})")
                else:
                    updated_count += 1
                    self.stdout.write(f"✓ {mun_name} ({zip_code}) mis à jour")

            self.stdout.write(self.style.SUCCESS(
                f"\nImportation terminée : {created_count} créations, {updated_count} mises à jour"
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\nERREUR : {str(e)}"))
            import traceback
            traceback.print_exc()