# Django WebSocket 聊天系統
一個基於 Django Channels 的即時聊天系統(使用 Redis 作為 Channel Layer)，支援多人聊天、訊息已讀狀態追蹤和聊天室管理功能。

## 功能特色
🔐 使用者認證：Django 內建認證系統

💬 即時聊天：WebSocket 即時訊息傳輸

👥 多人聊天室：支援多使用者同時聊天

✅ 已讀狀態：追蹤訊息已讀/未讀狀態

📖 歷史訊息：載入聊天室歷史記錄

🎯 視窗焦點偵測：自動標記已讀訊息

📝 聊天室管理：自動建立和管理聊天室

### 核心功能說明
#### 已讀狀態追蹤
- 發送者自動標記為已讀
- 視窗獲得焦點時自動標記訊息為已讀
- 即時更新所有使用者的已讀/未讀計數

#### 聊天室管理
- 聊天室不存在時自動建立
- 處理同時建立相同聊天室的競爭條件
- 聊天室操作日誌記錄

#### 歷史訊息
- 載入最新 50 則歷史訊息
- 自動標記已讀狀態
- 按時間順序顯示

#### 日誌功能
系統包含聊天室操作日誌記錄：
- 🆕 房間建立
- ✅ 房間查詢
- ⚠️ 建立衝突
- ❌ 錯誤情況

## 技術架構
- 後端: Django + Django Channels
- 前端: HTML + JavaScript + WebSocket
- 資料庫: Django ORM (預設 SQLite)
- 即時通訊: WebSocket

## 專案結構
```
Chat_Project
├──Chat_Project
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py
│   └── settings.py
├──chat/
│   ├── models.py          # 資料模型 (Room, Message)
│   ├── views.py           # 網頁視圖和 API
│   ├── consumers.py       # WebSocket 消費者
│   ├── routing.py         # WebSocket 路由設定
│   ├── urls.py            # HTTP 路由設定
│   ├── admin.py           # Django 管理界面
│   └── templates/chat/
│       ├── login.html    # 登入頁面
│       └── chat.html     # 聊天室頁面
├── logs/
├── utils/
│    └── logger.py     # 日誌記錄工具
├── db.splite3
├── manage.py
└── run.py
```

## 資料模型
### Room (聊天室)
`name`: 聊天室名稱

`participants`: 參與者 (多對多關聯)

### Message (訊息)
`room`: 所屬聊天室

`sender`: 發送者

`content`: 訊息內容

`timestamp`: 發送時間

`is_read`: 是否已讀 (棄用，使用 read_by 替代)

`read_by`: 已讀使用者列表 (多對多關聯)

## API 端點
### HTTP 路由
`GET` `/login/` - 登入頁面

`POST` `/login/` - 處理登入

`GET` `/logout/` - 登出

`GET` `/chat/` - 聊天室頁面

`GET` `/chat/messages/<room_name>/` - 獲取歷史訊息

### WebSocket 路由
`ws://localhost:5002/ws/chat/<room_name>/` - 聊天室 WebSocket 連線









