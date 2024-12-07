from django.contrib.auth.backends import BaseBackend
from django.contrib import messages
import psycopg2
from django.conf import settings

class PhoneNumberBackend(BaseBackend):
    def authenticate(self, request, phone_number=None, password=None):
        user_phone = request.session.get('user_phone')

        if not user_phone:
            messages.error(request, "You need to log in first.")
            return None

        try:
            with psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT']
            ) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM main_user WHERE phone_number = %s", (user_phone,))
                    user_data = cursor.fetchone()
                    
                    if not user_data:
                        messages.error(request, "User not found.")
                        return None

                    user = {
                        'id': user_data[0],
                        'name': user_data[1],
                        'password': user_data[2]
                    }

                    cursor.execute("SELECT EXISTS(SELECT 1 FROM main_worker WHERE user_ptr_id = %s)", (user_data[0],))
                    is_worker = cursor.fetchone()[0]
                    
                    user['is_worker'] = is_worker
                    
                    return user
                
        except Exception as e:
            print(f"Authentication error: {e}")
            messages.error(request, "An error occurred during authentication.")
            return None

    def get_user(self, user_id):
        try:
            with psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT']
            ) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM main_user WHERE id = %s", (user_id,))
                    user_data = cursor.fetchone()
                    
                    if user_data:
                        user = {
                            'id': user_data[0],
                            'name': user_data[1],  # Assuming name is the second field
                            'password': user_data[2]
                        }
                        return user
                    return None
        except Exception as e:
            print(f"Get user error: {e}")
            return None