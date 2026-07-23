import re
import logging
from enum import IntEnum
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger("moderation")


class UserRole(IntEnum):
    USER = 1
    MODERATOR = 2
    ADMIN = 3


@dataclass
class User:
    username: str
    role: UserRole = UserRole.USER



ROLE_REQUIRED = {
    "kick": UserRole.MODERATOR,
    "mute": UserRole.MODERATOR,
    "warn": UserRole.MODERATOR,
    "ban": UserRole.ADMIN,
}

WARNINGS_BEFORE_AUTO_BAN = 3

BANNED_WORDS = ["дурень", "ідіот", "бовдур", "тупиця", "адмін лох"]

_DURATION_UNITS = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days"}
_DURATION_PATTERN = re.compile(r"^(\d+)([smhd])$")


class ModerationManager:

    def __init__(self):
        self.banned_users: set[str] = set()
        self.muted_until: dict[str, datetime] = {}
        self.warnings: dict[str, int] = {}
        self.action_log: list[dict] = []

    def is_banned(self, username: str) -> bool:
        return username in self.banned_users

    def is_muted(self, username: str) -> bool:
        until = self.muted_until.get(username)
        if until is None:
            return False
        if datetime.now() >= until:
            del self.muted_until[username]
            return False
        return True

    def mute_time_left(self, username: str) -> timedelta | None:
        until = self.muted_until.get(username)
        if until is None:
            return None
        return max(until - datetime.now(), timedelta(0))

    def check_permission(self, actor: User, command: str) -> bool:
        required = ROLE_REQUIRED.get(command)
        if required is None:
            return False
        return actor.role >= required

    def parse_command(self, text: str) -> tuple[str, str | None, str] | None:
        if not text.startswith("/"):
            return None
        parts = text[1:].strip().split(maxsplit=2)
        if not parts:
            return None
        command = parts[0].lower()
        target = parts[1] if len(parts) > 1 else None
        reason = parts[2] if len(parts) > 2 else ""
        return command, target, reason

    def _parse_duration(self, duration_str: str) -> timedelta:
        match = _DURATION_PATTERN.match(duration_str)
        if not match:
            raise ValueError(
                f"Некоректний формат тривалості: '{duration_str}'. "
                f"Приклади: 30s, 10m, 1h, 2d"
            )
        value, unit = match.groups()
        return timedelta(**{_DURATION_UNITS[unit]: int(value)})

    def execute_command(self, actor: User, raw_command: str) -> str:
        parsed = self.parse_command(raw_command)
        if parsed is None:
            return "Це не команда модерації."

        command, target, reason = parsed

        if command not in ROLE_REQUIRED:
            return f"Невідома команда: /{command}"

        if not self.check_permission(actor, command):
            self._log(actor.username, command, target, reason, success=False, note="недостатньо прав")
            return f"⛔ У вас недостатньо прав для /{command} (потрібна роль: {ROLE_REQUIRED[command].name})."

        if target is None:
            return f"Вкажіть користувача: /{command} <username> [причина]"

        if command == "kick":
            result = f"Користувача {target} кікнуто з чату. Причина: {reason or 'не вказана'}"

        elif command == "ban":
            self.banned_users.add(target)
            result = f"Користувача {target} назавжди забанено. Причина: {reason or 'не вказана'}"

        elif command == "mute":
            duration_str, _, real_reason = reason.partition(" ")
            try:
                duration = self._parse_duration(duration_str) if duration_str else timedelta(minutes=10)
            except ValueError as e:
                return str(e)
            until = datetime.now() + duration
            self.muted_until[target] = until
            result = f"Користувача {target} заглушено до {until.strftime('%H:%M:%S')} ({real_reason or 'причина не вказана'})."

        elif command == "warn":
            self.warnings[target] = self.warnings.get(target, 0) + 1
            count = self.warnings[target]
            result = f"Користувачу {target} видано попередження ({count}/{WARNINGS_BEFORE_AUTO_BAN}). Причина: {reason or 'не вказана'}"
            if count >= WARNINGS_BEFORE_AUTO_BAN:
                self.banned_users.add(target)
                result += f" — ліміт попереджень вичерпано, {target} автоматично забанено."

        else:
            result = f"Невідома команда: /{command}"

        self._log(actor.username, command, target, reason, success=True)
        return result

    def filter_message(self, text: str) -> tuple[str, bool]:
        found = False

        def _mask(match: re.Match) -> str:
            nonlocal found
            found = True
            return "*" * len(match.group())

        pattern = r"\b(" + "|".join(re.escape(w) for w in BANNED_WORDS) + r")\b"
        filtered = re.sub(pattern, _mask, text, flags=re.IGNORECASE)
        return filtered, found

    def _log(self, moderator: str, action: str, target: str | None, reason: str, success: bool, note: str = ""):
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "moderator": moderator,
            "action": action,
            "target": target,
            "reason": reason,
            "success": success,
            "note": note,
        }
        self.action_log.append(entry)
        status = "OK" if success else "DENIED"
        logger.info(f"[{status}] {moderator} -> /{action} {target} ({reason}) {note}".strip())