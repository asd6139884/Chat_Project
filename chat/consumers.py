import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Chat_Project.settings")
django.setup()


from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth.models import User
from .models import Room, Message
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from utils.logger import log_room_action


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name'] #從 URL 中取出聊天室名稱
        self.room_group_name = f'chat_{self.room_name}' # 聊天室群組名稱

        # 使用異步 ORM 方法 獲取或創建聊天室
        try: # 查詢聊天室
            self.room = await Room.objects.aget(name=self.room_name)
            log_room_action(self.room_name, 'get')
        except ObjectDoesNotExist: # 如果聊天室不存在，則創建一個新的房間
            try: # 嘗試創建聊天室
                self.room = await Room.objects.acreate(name=self.room_name)
                log_room_action(self.room_name, 'create')
            except IntegrityError: # 如果創建失敗，可能是因為其他人已經創建了同名聊天室，重新查一次
                self.room = await Room.objects.aget(name=self.room_name)
                log_room_action(self.room_name, 'conflict')

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        # 判斷訊息類型
        if data.get("type") == "read_messages":
            await self.handle_read_messages(data)
        else:
            await self.handle_chat_message(data)

    async def handle_chat_message(self, data):
        message = data['message']
        sender_username  = data['sender']  # 從前端傳入
        sender_user = await sync_to_async(User.objects.get)(username=sender_username)

        # 儲存訊息並將發送者標記為已讀
        msg_obj = await sync_to_async(Message.objects.create)(
            room=self.room,
            sender=sender_user,
            content=message
        )
        await sync_to_async(msg_obj.read_by.add)(sender_user) # 發送者標記為已讀
        
        # 計算總使用者數量與未讀數（聊天室參與者）
        total_users = await sync_to_async(lambda: self.room.participants.count())()
        if total_users == 0:
            total_users = 1  # fallback 避免除以 0 或出現負值
        read_count = 1  # 目前只有 sender 自己已讀
        unread_count = max(total_users - read_count, 0)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_username,
                'read_count': 1,
                'unread_count': unread_count,
                'message_id': msg_obj.id
            }
        )

    async def handle_read_messages(self, data):
        message_ids = data.get('message_ids', [])
        user = self.scope["user"]

        for msg_id in message_ids:
            try:
                msg = await sync_to_async(Message.objects.get)(id=msg_id)
                await sync_to_async(msg.read_by.add)(user)
                read_count = await sync_to_async(msg.read_by.count)()

                total_users = await sync_to_async(lambda: msg.room.participants.count())()
                if total_users == 0:
                    total_users = 1
                unread_count = max(total_users - read_count, 0)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'read_update',
                        'message_id': msg_id,
                        'read_count': read_count,
                        'unread_count': unread_count
                    }
                )
            except Message.DoesNotExist:
                print(f"⚠️ Message {msg_id} 不存在")
                continue

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender'],
            'read_count': event['read_count'],
            'unread_count': event['unread_count'],
            'message_id': event['message_id']
        }))

    async def read_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read_update',
            'message_id': event['message_id'],
            'read_count': event['read_count'],
            'unread_count': event['unread_count']
        }))
