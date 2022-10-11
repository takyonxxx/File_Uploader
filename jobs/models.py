from django.db import models


# Create your models here.

class AuditLogs(models.Model):
    id = models.CharField(max_length=50, primary_key=True, editable=False)
    clients = models.JSONField()
    ip_address = models.CharField(max_length=50)
    last_access = models.DateTimeField()
    start = models.DateTimeField()
    user_id = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
