"""
WebSocket URL routing (like urls.py but for WebSocket)

What it does:
- Defines which WebSocket URLs go to which consumers
- Just like Django URL routing but for WebSocket
"""

from django.urls import re_path
from . import consumers


websocket_urlpatterns = [
  # When user connects to ws://server/ws/jobs/
  # Send them To JobConsumer
  re_path(r'ws/job/$', consumers.JobConsumer.as_asgi()),
]

# re_path(r'ws/jobs/$', consumers.JobConsumer.as_asgi())
    #     └─ regex pattern ─┘ └─ sends to this consumer ─┘

#Matches: ws://localhost/ws/jobs/
#Doesn't match: ws://localhost/jobs/  (missing /ws/)