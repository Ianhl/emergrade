import json, time
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

# Simple in-memory last-focus per session (good enough for demo)
_LAST_FOCUS = {}

class MuseConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        self.group = f"telemetry-{self.session_id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({"type":"status","message":"muse_ws_connected","session":self.session_id}))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Expect JSON messages from the bridge script
        try:
            msg = json.loads(text_data or "{}")
        except Exception:
            return

        kind = msg.get("kind")
        if kind == "muse_features":
            # Update last focus and live-broadcast (optional)
            focus = float(msg.get("focus", 0.5))
            _LAST_FOCUS[self.session_id] = focus
            await self.channel_layer.group_send(self.group, {
                "type": "telemetry_event",
                "payload": {"v":1,"kind":"muse_tick","ts":msg.get("ts", time.time()),"focus":focus}
            })

        elif kind == "muse_summary":
            # Final summary payload from the bridge → broadcast as "model"
            focus = float(msg.get("focus", 0.5))
            _LAST_FOCUS[self.session_id] = focus
            await self.channel_layer.group_send(self.group, {
                "type": "telemetry_event",
                "payload": {"v":1,"kind":"model","source":"muse","focus":focus,
                            "alpha":msg.get("alpha"),"beta":msg.get("beta"),"theta":msg.get("theta")}
            })

        elif msg.get("type") == "get_latest":
            # Allow browser to pull the current focus when image finishes
            focus = float(_LAST_FOCUS.get(self.session_id, 0.5))
            await self.send(text_data=json.dumps({"v":1,"kind":"model","source":"muse","focus":focus}))

    async def telemetry_event(self, event):
        await self.send(text_data=json.dumps(event["payload"]))
