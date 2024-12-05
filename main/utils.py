# main/utils.py
import psycopg2
from django.conf import settings

def get_user_name(user_id):
    try:
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT name FROM main_user WHERE id = %s", (user_id,))
                user_data = cursor.fetchone()
                if user_data:
                    return user_data[0]
    except Exception as e:
        print(f"Error fetching user name: {e}")
    return None