from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse

from moderation import ModerationManager, UserRole
from connection_manager import ConnectionManager

app = FastAPI(title="Moderated Chat (WebSocket)")

manager = ConnectionManager()
moderation = ModerationManager()

ROLE_MAP = {
    "user": UserRole.USER,
    "moderator": UserRole.MODERATOR,
    "admin": UserRole.ADMIN,
}

CLOSE_BANNED = 4003
CLOSE_KICKED = 4001


@app.get("/")
def get_test_page():
    return HTMLResponse(TEST_CLIENT_HTML)


@app.websocket("/ws/{username}")
async def websocket_endpoint(
    websocket: WebSocket,
    username: str,
    role: str = Query("user", description="user | moderator | admin — лише для демо; у бойовому проєкті роль береться з БД/токена"),
):
    if moderation.is_banned(username):
        await websocket.close(code=CLOSE_BANNED)
        return

    user_role = ROLE_MAP.get(role.lower(), UserRole.USER)
    await manager.connect(websocket, username, user_role)
    await manager.broadcast(f"🔵 {username} приєднався до чату ({user_role.name}).")

    try:
        while True:
            text = await websocket.receive_text()

            if moderation.is_banned(username):
                await websocket.send_text("[Система] Вас забанено. З'єднання розірвано.")
                await websocket.close(code=CLOSE_BANNED)
                manager.disconnect(username)
                break

            if text.startswith("/"):
                actor = manager.users[username]
                parsed = moderation.parse_command(text)
                result = moderation.execute_command(actor, text)
                await websocket.send_text(f"[Система] {result}")

                if parsed and moderation.check_permission(actor, parsed[0]):
                    command, target, reason = parsed
                    if command in ("kick", "ban") and target in manager.active:
                        close_code = CLOSE_BANNED if command == "ban" else CLOSE_KICKED
                        disconnected = await manager.force_disconnect(target, reason, close_code)
                        if disconnected:
                            await manager.broadcast(
                                f"⚠️ {target} видалено з чату модератором {username} ({command})."
                            )
                continue

            if moderation.is_muted(username):
                left = moderation.mute_time_left(username)
                await websocket.send_text(
                    f"[Система] 🔇 Ви заглушені ще {int(left.total_seconds())} сек."
                )
                continue

            filtered_text, was_filtered = moderation.filter_message(text)
            suffix = " (відредаговано фільтром)" if was_filtered else ""
            await manager.broadcast(f"{username}: {filtered_text}{suffix}")

    except WebSocketDisconnect:
        manager.disconnect(username)
        await manager.broadcast(f"🔴 {username} покинув чат.")


TEST_CLIENT_HTML = """
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <title>Тестовий чат-клієнт</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; }
        #log { border: 1px solid #ccc; height: 300px; overflow-y: auto; padding: 10px; margin-bottom: 10px; }
        #log div { margin-bottom: 4px; }
        input { padding: 6px; }
        #username, #role { width: 120px; }
        #message { width: 300px; }
    </style>
</head>
<body>
    <h2>Тестовий чат-клієнт (WebSocket)</h2>
    <div>
        Username: <input id="username" value="alice">
        Role: <select id="role">
            <option value="user">user</option>
            <option value="moderator">moderator</option>
            <option value="admin">admin</option>
        </select>
        <button onclick="connect()">Підключитись</button>
    </div>
    <br>
    <div id="log"></div>
    <input id="message" placeholder="Повідомлення або /kick user причина" onkeydown="if(event.key==='Enter') send()">
    <button onclick="send()">Надіслати</button>

    <script>
        let ws = null;

        function log(text) {
            const div = document.createElement("div");
            div.textContent = text;
            document.getElementById("log").appendChild(div);
            document.getElementById("log").scrollTop = 1e9;
        }

        function connect() {
            const username = document.getElementById("username").value;
            const role = document.getElementById("role").value;
            if (ws) ws.close();
            ws = new WebSocket(`ws://${location.host}/ws/${username}?role=${role}`);
            ws.onopen = () => log(`--- З'єднано як ${username} (${role}) ---`);
            ws.onmessage = (e) => log(e.data);
            ws.onclose = (e) => log(`--- З'єднання закрито (код ${e.code}) ---`);
        }

        function send() {
            const input = document.getElementById("message");
            if (ws && input.value) {
                ws.send(input.value);
                input.value = "";
            }
        }
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)