from django.db import models

class SystemMetric(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_percent = models.FloatField()
    memory_percent = models.FloatField()
    disk_percent = models.FloatField()
    
    class Meta:
        ordering = ['-timestamp']