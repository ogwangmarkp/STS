from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings

# Create your models here.


class User(AbstractUser):
    date_added = models.DateTimeField(default = timezone.now)
    updated_password = models.BooleanField(default=False)
    email         = models.EmailField(max_length = 255, null=True, blank=True)
    phone_number  =  models.CharField(max_length=25, null=True, blank=True)

    class Meta:
        db_table = 'public\".\"user' 
    
 