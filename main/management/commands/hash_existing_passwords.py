from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.conf import settings
import psycopg2

class Command(BaseCommand):
    help = 'Hashes existing plain text passwords in the User model'

    def handle(self, *args, **kwargs):
        try:
            conn = psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT']
            )
            cursor = conn.cursor()
            cursor.execute("SELECT id, phone_number, password FROM main_user")
            users = cursor.fetchall()

            for user in users:
                user_id, phone_number, password = user
                if not password.startswith('pbkdf2_'):  # Check if the password is already hashed
                    hashed_password = make_password(password)
                    cursor.execute(
                        "UPDATE main_user SET password = %s WHERE id = %s",
                        (hashed_password, user_id)
                    )
                    self.stdout.write(self.style.SUCCESS(f'Password hashed for user: {phone_number}'))

            conn.commit()
            cursor.close()
            conn.close()
            self.stdout.write(self.style.SUCCESS('All passwords have been hashed.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error hashing passwords: {e}'))