from fastapi import WebSocket
from moderation import User, UserRole


class ConnectionManager:

    def __init__(self):
        self.active: dict[str, WebSocket] = {}
        self.users: dict[str, User] = {}

    async def connect(self, websocket: WebSocket, username: str, role: UserRole) -> None:
        await websocket.accept()
        self.active[username] = websocket
        self.users[username] = User(username=username, role=role)

    def disconnect(self, username: str) -> None:
        self.active.pop(username, None)
        self.users.pop(username, None)

    async def send_personal(self, username: str, message: str) -> None:
        ws = self.active.get(username)
        if ws is not None:
            await ws.send_text(message)

    async def broadcast(self, message: str, exclude: str | None = None) -> None:
        for username, ws in list(self.active.items()):
            if username != exclude:
                await ws.send_text(message)

    async def force_disconnect(self, username: str, reason: str, close_code: int = 4000) -> bool:
        ws = self.active.get(username)
        if ws is None:
            return False
        await ws.send_text(f"[Система] Вас від'єднано від чату. Причина: {reason or 'не вказана'}")
        await ws.close(code=close_code)
        self.disconnect(username)
        return True