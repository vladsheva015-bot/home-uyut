import re
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from app.schemas import Priority, Source


MOSCOW_TZ = ZoneInfo("Europe/Moscow")
URGENCY_PATTERN = re.compile(r"(?<!\w)(?:срочно|сегодня|asap|горит)(?!\w)", re.IGNORECASE)


def now_moscow() -> datetime:
    return datetime.now(MOSCOW_TZ)


def calculate_priority(
    *, source: Source, text: str, amount: Decimal | None, created_at: datetime
) -> Priority:
    local_time = created_at.astimezone(MOSCOW_TZ).time()
    in_telegram_working_hours = (
        source == Source.TELEGRAM
        and (local_time.hour, local_time.minute, local_time.second) >= (9, 0, 0)
        and (local_time.hour, local_time.minute, local_time.second) < (18, 0, 0)
    )

    if (
        (amount is not None and amount >= Decimal("100000"))
        or URGENCY_PATTERN.search(text)
        or in_telegram_working_hours
    ):
        return Priority.HIGH

    if (amount is not None and amount >= Decimal("30000")) or (
        source == Source.SITE and amount is not None and amount >= Decimal("10000")
    ):
        return Priority.MEDIUM

    return Priority.LOW