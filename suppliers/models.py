from django.db import models
from django.utils import timezone
from django.conf import settings

# Create your models here.


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    email = models.EmailField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    phone_number_2 = models.CharField(max_length=15, null=True, blank=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='supplier_added_by')

    class Meta:
        db_table = 'public\".\"supplier' 
