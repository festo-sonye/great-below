from django.core.management.base import BaseCommand
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Fix usernames to match emails for all users'

    def handle(self, *args, **options):
        users = CustomUser.objects.all()
        count = 0
        for user in users:
            if user.username != user.email:
                user.username = user.email
                user.save()
                count += 1
                self.stdout.write(f'Fixed: {user.email}')
        
        self.stdout.write(self.style.SUCCESS(f'✅ Fixed {count} users'))
