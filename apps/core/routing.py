from channels.routing import route
from apps.core.consumers import ws_message
channel_routing = [
    route("websocket.receive", ws_message, path="^/"),
]
