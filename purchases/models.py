from django.db import models
from django.utils import timezone
from django.conf import settings
from suppliers.models import Supplier
# Create your models here.


class Stock(models.Model):
    quantity = models.FloatField(default=0.0)
    price = models.FloatField(default=0.0)
    record_date = models.DateTimeField(default=timezone.now)
    date_added = models.DateTimeField(default=timezone.now)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name='stock_supplier')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stock_added_by')

    class Meta:
        db_table = 'public\".\"stock' 

class Purchase(models.Model):
    amount = models.FloatField(default=0.0)
    record_date = models.DateTimeField(default=timezone.now)
    date_added = models.DateTimeField(default=timezone.now)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name='purchase_supplier')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchase_added_by')

    class Meta:
        db_table = 'public\".\"purchase' 