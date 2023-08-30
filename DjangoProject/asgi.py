"""
ASGI config for DjangoProject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from your_app.consumers import YourWebSocketConsumer 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        # 添加 WebSocket 的路由配置
    ),
})

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        [
            # 添加 WebSocket 路由
            YourWebSocketConsumer.as_asgi(),
        ],
    ),
})
