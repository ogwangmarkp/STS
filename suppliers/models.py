from django.db import models
from django.utils import timezone
from django.conf import settings
from locations.models import Location
# Create your models here.


class Supplier(models.Model):
    supplier_no = models.CharField(max_length=255,null=True, blank=True)
    name = models.CharField(max_length=255)
    date_added = models.DateTimeField(default=timezone.now)
    email = models.EmailField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    phone_number_2 = models.CharField(max_length=15, null=True, blank=True)
    address = models.ForeignKey(Location, null=True, blank=True,on_delete=models.CASCADE, related_name='supplier_location')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='supplier_added_by')

    class Meta:
        db_table = 'public\".\"supplier' 
