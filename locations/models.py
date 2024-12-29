from django.db import models
from django.utils import timezone
from django.conf import settings

# Create your models here.


class Location(models.Model):
    address = models.CharField(max_length=255, null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='location_added_by')

    class Meta:
        db_table = 'public\".\"location' 
