from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'List all superusers'

    def handle(self, *args, **options):
        User = get_user_model()
        superusers = User.objects.filter(is_superuser=True)
        
        if superusers:
            self.stdout.write("List of superusers:")
            for user in superusers:
                self.stdout.write(f"- {user.username} ({user.email})")
        else:
            self.stdout.write("No superusers found.")