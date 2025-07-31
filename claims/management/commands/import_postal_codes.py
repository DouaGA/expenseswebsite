import json
from django.core.management.base import BaseCommand
from claims.models import Municipality, Wilaya

class Command(BaseCommand):
    help = 'Import postal codes from JSON into Municipality model'

    def handle(self, *args, **kwargs):
        json_file_path = 'claims/data/zip-postcodes.json'  # Chemin relatif depuis manage.py
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                # Créer ou récupérer la Wilaya
                wilaya, _ = Wilaya.objects.get_or_create(
                    name=item['Gov'],
                    defaults={'code': item['Gov'][:2]}  # Exemple: extraire le code de Gov
                )
                # Créer ou mettre à jour la Municipalité
                Municipality.objects.update_or_create(
                    postal_code=item['zip'],
                    defaults={
                        'name': item['Cite'],
                        'wilaya': wilaya,
                        'delegation': item['Deleg'],
                        'code': item['zip'][:3]  # Exemple: utiliser les 3 premiers chiffres du code postal
                    }
                )
        self.stdout.write(self.style.SUCCESS('Données importées avec succès !'))