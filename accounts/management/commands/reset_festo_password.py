from django.core.management.base import BaseCommand
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Reset Festo password'

    def handle(self, *args, **options):
        festo = CustomUser.objects.filter(email='festo@example.com').first()
        if festo:
            festo.set_password('password123')
            festo.save()
            self.stdout.write(self.style.SUCCESS('✅ Password reset for festo@example.com to: password123'))
        else:
            self.stdout.write(self.style.ERROR('❌ Festo not found'))
