from django.db import models
from django.utils import timezone
from django.conf import settings
from customers.models import Customer
# Create your models here.

class StockDelivered(models.Model):
    quantity = models.FloatField(default=0.0)
    price = models.FloatField(default=0.0)
    record_date = models.DateTimeField(default=timezone.now)
    date_added = models.DateTimeField(default=timezone.now)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='sd_customer')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sd_added_by')

    class Meta:
        db_table = 'public\".\"stock_delivered' 

class Sale(models.Model):
    amount = models.FloatField(default=0.0)
    record_date = models.DateTimeField(default=timezone.now)
    date_added = models.DateTimeField(default=timezone.now)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='sales_customer')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sale_added_by')

    class Meta:
        db_table = 'public\".\"sale' 