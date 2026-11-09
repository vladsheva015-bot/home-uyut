import csv
from collections import Counter
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from app.priority import calculate_priority
from app.schemas import Priority, Source


def timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value)


@pytest.mark.parametrize(
    ("source", "text", "amount", "created_at", "expected"),
    [
        (Source.AVITO, "Нужен диван", Decimal("100000"), "2026-11-09T19:00:00+03:00", Priority.HIGH),
        (Source.AVITO, "Нужен диван", Decimal("99999"), "2026-11-09T19:00:00+03:00", Priority.MEDIUM),
        (Source.AVITO, "Нужен стол", Decimal("30000"), "2026-11-09T19:00:00+03:00", Priority.MEDIUM),
        (Source.AVITO, "Нужен стол", Decimal("29999"), "2026-11-09T19:00:00+03:00", Priority.LOW),
        # Сайт с суммой от 10000 теперь дает MEDIUM, а меньше — LOW
        (Source.SITE, "Нужна банкетка", Decimal("10000"), "2026-11-09T19:00:00+03:00", Priority.MEDIUM),
        (Source.SITE, "Мелкая покупка", Decimal("5000"), "2026-11-09T19:00:00+03:00", Priority.LOW),
        (Source.AVITO, "Need a sofa ASAP", Decimal("1000"), "2026-11-09T19:00:00+03:00", Priority.HIGH),
        (Source.AVITO, "Несрочно, уточняю", Decimal("1000"), "2026-11-09T19:00:00+03:00", Priority.LOW),
        (Source.TELEGRAM, "Нужна полка", None, "2026-11-09T08:59:00+03:00", Priority.LOW),
        (Source.TELEGRAM, "Нужна полка", None, "2026-11-09T09:00:00+03:00", Priority.HIGH),
        (Source.TELEGRAM, "Нужна полка", None, "2026-11-09T17:59:00+03:00", Priority.HIGH),
        (Source.TELEGRAM, "Нужна полка", None, "2026-11-09T18:00:00+03:00", Priority.LOW),
    ],
)
def test_calculate_priority_boundaries(source, text, amount, created_at, expected):
    assert calculate_priority(
        source=source,
        text=text,
        amount=amount,
        created_at=timestamp(created_at),
    ) == expected


def test_csv_has_30_valid_leads_and_expected_priority_distribution():
    csv_path = Path(__file__).parents[1] / "data" / "leads.csv"
    with csv_path.open(encoding="utf-8", newline="") as file:
        leads = list(csv.DictReader(file))

    priorities = [
        calculate_priority(
            source=Source(lead["source"]),
            text=lead["text"],
            amount=Decimal(lead["amount"]) if lead["amount"] else None,
            created_at=timestamp(lead["created_at"]),
        )
        for lead in leads
    ]

    assert len(leads) == 30
    assert [lead["id"] for lead in leads] == [str(number) for number in range(1, 31)]
    assert Counter(priorities) == Counter(
        {Priority.HIGH: 12, Priority.MEDIUM: 8, Priority.LOW: 10}
    )
