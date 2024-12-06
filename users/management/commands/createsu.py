from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        if not get_user_model().objects.filter(username="admin2024").exists():
          

            saved_user = User.objects.create(**{
                "first_name":"admin2024",
                "username":"admin2024",
                "password":"root@admin2024"
            })


                
           
            