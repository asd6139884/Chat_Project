from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Room, Message

# 登入
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('chat_room')  # 替換成聊天室頁面的 URL 名稱
        else:
            return render(request, 'chat/login.html', {'error': '帳號或密碼錯誤'})
    return render(request, 'chat/login.html')

# 登出
def logout_view(request):
    logout(request)
    return redirect('login')

# 聊天室畫面
@login_required
def chat_room(request):
    return render(request, 'chat/chat.html', {'username': request.user.username})

# 回傳歷史訊息 API，並標記為已讀
@login_required
def chat_messages_api(request, room_name):
    try:
        room = Room.objects.get(name=room_name)
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)

    # 抓最新 50 則訊息
    messages = Message.objects.filter(room=room).order_by('-timestamp')[:50]
    messages = reversed(messages)  # 轉成由舊到新

    total_users = room.participants.count() if room.participants.exists() else 1

    data = []
    for msg in messages:
        # 加入目前使用者為已讀（如果還沒的話）
        if not msg.read_by.filter(id=request.user.id).exists():
            msg.read_by.add(request.user)
        
        data.append({
            'id': msg.id,
            'sender': msg.sender.username,
            'message': msg.content,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'read_count': msg.read_by.count(),
            'unread_count': total_users - msg.read_by.count()
        })

    return JsonResponse({'messages': data})


