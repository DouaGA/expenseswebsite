from django.core.management.base import BaseCommand
from core.models import PostalCode, Municipality, Wilaya
import json
from pathlib import Path
import os

class Command(BaseCommand):
    help = 'Importe les codes postaux et municipalités'

    def handle(self, *args, **options):
        # Chemin absolu vérifié
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        json_path = base_dir / 'core' / 'templates' / 'core' / 'data' / 'zip-postcodes.json'
        
        self.stdout.write(f"Chemin utilisé : {json_path}")

        # Vérification explicite du fichier
        if not json_path.exists():
            self.stdout.write(self.style.ERROR("\nFichier introuvable !"))
            self.stdout.write("Structure trouvée dans le projet :")
            for f in base_dir.glob('**/*.json'):
                self.stdout.write(f"→ {f}")
            return

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                postal_data = json.load(f)
                
            created_count = 0
            
            for item in postal_data:
                # Création Wilaya
                wilaya, _ = Wilaya.objects.get_or_create(
                    name=item['Gov'],
                    defaults={'code': item['zip'][:2]}
                )
                
                # Nettoyage nom municipalité
                mun_name = ' '.join(item['Cite'].split('-')[0].strip().split())
                
                # Création PostalCode
                postal_code, pc_created = PostalCode.objects.get_or_create(
                    zip_code=item['zip'],
                    defaults={
                        'gov': item['Gov'],
                        'deleg': item['Deleg'],
                        'cite': item['Cite']
                    }
                )
                
                # Création Municipality
                mun, mun_created = Municipality.objects.get_or_create(
                    name=mun_name,
                    postal_code=item['zip'],
                    defaults={'wilaya': wilaya}
                )
                
                if mun_created:
                    created_count += 1
                    self.stdout.write(f"+ {mun_name} ({item['zip']})")

            self.stdout.write(self.style.SUCCESS(f"\nImportation réussie ! {created_count} nouvelles municipalités créées."))
            self.stdout.write(f"Total Municipalités: {Municipality.objects.count()}")
            self.stdout.write(f"Total Codes Postaux: {PostalCode.objects.count()}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\nERREUR : {str(e)}"))
            self.stdout.write("Vérifiez le format du fichier JSON !")