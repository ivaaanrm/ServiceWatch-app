from django.contrib import admin

# Register your models here.
from .models import SystemMetric


class SystemMetricAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'cpu_percent', 'memory_percent', 'disk_percent')  # Columns to display
    list_filter = ('timestamp',)  # Filter by timestamp
    ordering = ('-timestamp',)  # Show latest entries first
    search_fields = ('timestamp',)  # Enable searching by timestamp

admin.site.register(SystemMetric, SystemMetricAdmin)

