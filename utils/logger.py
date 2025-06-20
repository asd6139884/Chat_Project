import logging

logger = logging.getLogger('chat')

def log_room_action(room_name: str, action: str):
    emoji_map = {
        'create': ('🆕', 'info'),
        'get': ('✅', 'info'),
        'conflict': ('⚠️', 'warning'),
        'error': ('❌', 'error'),
    }

    emoji, level = emoji_map.get(action, ('ℹ️', 'info'))
    msg = f"{emoji} 房間處理：「{room_name}」，動作：{action.upper()}"

    log_method = getattr(logger, level)
    log_method(msg)
