from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from main.models import User

class Command(BaseCommand):
    help = 'Hashes existing plain text passwords in the User model'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        for user in users:
            if not user.password.startswith('pbkdf2_'):  # Check if the password is already hashed
                user.password = make_password(user.password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Password hashed for user: {user.phone_number}'))
        self.stdout.write(self.style.SUCCESS('All passwords have been hashed.'))