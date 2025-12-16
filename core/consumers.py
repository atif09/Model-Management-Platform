"""
WebSocket Consumer = handles WebSocket connections

What is a Consumer?
- Like a View, but for WebSocket instead of HTTP
- Handles: connect, disconnect, receive messages
- Can send messages to user or broadcast to group

Key Methods:
- connect() = when user connects
- disconnect() = when user disconnects  
- receive() = when user sends a message
- send() = send message to this user
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

class JobConsumer(AsyncWebsocketConsumer):
  # Handles websockt connections for job status updates

  # Each user gets their own instance of this consumer

  async def connect(self):
    self.user = self.scope['user']

    # Check if user is authenticated
    if isinstance(self, AnonymousUser):
      await self.close() # Dont allow unauthenticated users
      return 

    # Create group name based on user ID
    # This ensures each user only sees their own job updates
    self.group_name = f"user_{self.user.id}_jobs"

    # Add this connection to the group
    # Now this consumer will get all messages sent to this group
    await self.channel_layer.group_add(
      self.group_name,
      self.channel_name # This consumer's unique channel
    )

    # Acept the websocket connection
    # Without this, the connection closes
    await self.accept()

    # Send welcome message to the user
    await self.send(text_data=json.dumps({
      "type": 'connection_established',
      "message": f"Connected for user {self.user.username}"
    }))

  async def disconnect(self, close_code):
    # Remove from group so we dont send messages to offline users
    await self.channel_layer.group_discard(
      self.group_name,
      self.channel_name
    )

  async def receive(self, text_data):
    try:
      # Parse JSON message from client
      data = json.loads(text_data)
      message_type = data.get('type')

      # Handle different message types
      if message_type == 'ping':
        await self.send(text_data=json.dumps({
          'type': 'pong',
          'message': 'connection alive'
        }))

      else:
        # Unknown message type
        await self.send(text_data = json.dumps({
          'type': 'error',
          'message': f'Unknown message type: {message_type}'
        }))

    except json.JSONDecodeError:
      await self.send(text_data=json.dumps({
        'type': 'error',
        'message': 'Invalid JSON'
      }))


  # ==== Broadcast Handlers ====
  # These methods handle messages sent to this group
  # When we do: group_send('user_1_jobs', {'type': 'job_update', ...})
  # This method gets called 

  async def job_update(self, event):
    # Extract message data
    message = event.get('message', {})

    # Send to the WebSocket client
    await self.send(text_data=json.dumps({
      'type': 'job_update',
      'data': message
    }))

  async def job_completed(self, event):
    message = event.get('message', {})

    await self.send(text_data=json.dumps({
      'type': 'job_completed',
      'data': message
    }))

  async def job_failed(self, event):
    message = event.get('message', {})

    await self.send(text_data=json.dumps({
      'type': 'job_failed',
      'data': message
    }))

# async def connect(self):
    # "async" = this function doesn't block (can do other things)
    # "await" = wait for this operation to complete


# await self.channel_layer.group_add(group_name, channel_name)
# Adds this connection to a group
# So it receives all messages sent to that group

# async def job_update(self, event):
    # Automatically called when group receives 'job_update' type message
    # 'event' contains the broadcast message

  

