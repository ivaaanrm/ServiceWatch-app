import json
import asyncio
from pathlib import Path
import psutil
from channels.generic.websocket import AsyncWebsocketConsumer
import yaml
import os
import django
from asgiref.sync import sync_to_async

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ServiceWatch.settings")  # Replace with your actual project name
django.setup()

from .models import SystemMetric

class SystemStatsConsumer(AsyncWebsocketConsumer):
    SERVICES_FILE = Path(__file__).parent.parent.resolve() / "resources" / "config.yml" 

    async def connect(self):
        print("WebSocket connected")  # Debug print
        await self.accept()
        self.running = True
        asyncio.create_task(self.send_stats())

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected with code: {close_code}")  # Debug print
        self.running = False

    async def send_stats(self):
        while self.running:
            try:
                stats = await self.get_system_stats()
                await sync_to_async(SystemMetric.objects.create)(**stats)

                # Load service names from YAML asynchronously
                services_to_check = await sync_to_async(self.load_services)()
                stats['services'] = await asyncio.gather(
                    *[sync_to_async(self.get_service_status)(service) for service in services_to_check]
                )

                await self.send(text_data=json.dumps(stats))
                await asyncio.sleep(2)
            except Exception as e:
                print(f"Error in send_stats: {e}")  # Debug print
                self.running = False
                break

    @sync_to_async
    def get_system_stats(self):
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
        }

    def get_service_status(self, service_name):
        for proc in psutil.process_iter(['name', 'status']):
            try:
                if proc.info['name'] and service_name.lower() in proc.info['name'].lower():
                    return {'name': proc.info['name'], 'status': proc.info['status']}
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return {'name': service_name, 'status': 'not running'}

    def load_services(self):
        try:
            with open(self.SERVICES_FILE, "r") as file:
                data = yaml.safe_load(file)
                return data.get("services", [])  # Get the list of services
        except Exception as e:
            print(f"Error loading services.yaml: {e}")
            return []
