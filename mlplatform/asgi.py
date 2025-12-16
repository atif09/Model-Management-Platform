"""
ASGI config for mlplatform project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import get_asgi_application 
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlplatform.settings.dev')
django.setup()

# Import after Django setup

from core.consumers import JobConsumer

# Get Django ASGI app for HTTP requests
django_asgi_app = get_asgi_application()

# Define Websocket URL routes (like urls.py but for WebSocket)
websocket_urlpatterns = [


]

# Main ASGI application
application = ProtocolTypeRouter({
  # Handle HTTP requests normally (Djngo views)
  "http": django_asgi_app,

  # Handle WebSocket connections
  # AuthMiddlewareStack = authenticate user before allowing connection
  "websocket": AuthMiddlewareStack(
    URLRouter(
      websocket_urlpatterns
    )
  )
})

