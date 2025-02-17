
# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.timezone import now, timedelta
from .models import SystemMetric
from django.http.request import HttpRequest

def dashboard(request):
    return render(request, 'monitor/dashboard.html')

def get_system_metrics(request: HttpRequest):
    """API endpoint to fetch system metrics based on the selected time range."""
    time_range = request.GET.get("range", "live")  # Default to live data

    # Define time delta based on range
    time_deltas = {
        "10m": timedelta(minutes=10),
        "1h": timedelta(hours=1),
        "4h": timedelta(hours=4),
        "8h": timedelta(hours=8),
    }

    if time_range in time_deltas:
        start_time = now() - time_deltas[time_range]
        metrics = SystemMetric.objects.filter(timestamp__gte=start_time).order_by("timestamp")
        
        # For longer time ranges, reduce data points to prevent overwhelming the chart
        if time_range in ["4h", "8h"]:
            step = len(metrics) // 100 if len(metrics) > 100 else 1
            metrics = metrics[::step]
    else:
        # Default: Return only the latest data (live)
        metrics = SystemMetric.objects.order_by("-timestamp")[:30][::-1]  # Reverse order for correct time series

    data = {
        "timestamps": [m.timestamp.strftime("%H:%M:%S") for m in metrics],
        "cpu": [m.cpu_percent for m in metrics],
        "memory": [m.memory_percent for m in metrics],
        "disk": [m.disk_percent for m in metrics],
    }
    
    return JsonResponse(data)