import os
import django
import uvicorn

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Chat_Project.settings")
    django.setup()
    uvicorn.run("Chat_Project.asgi:application", host="0.0.0.0", port=5002, reload=True)
