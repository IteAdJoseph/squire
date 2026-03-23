from datetime import date

from app.admin.router import _next_due_date


def test_due_day_later_in_month() -> None:
    """today=Mar 5, due_day=15 → next_due=Mar 15"""
    today = date(2025, 3, 5)
    period_start, period_end, next_due = _next_due_date(15, _today=today)
    assert next_due == date(2025, 3, 15)
    assert period_start == today
    assert period_end == date(2025, 3, 14)


def test_due_day_already_passed() -> None:
    """today=Mar 20, due_day=15 → next_due=Apr 15"""
    today = date(2025, 3, 20)
    period_start, period_end, next_due = _next_due_date(15, _today=today)
    assert next_due == date(2025, 4, 15)
    assert period_start == today
    assert period_end == date(2025, 4, 14)


def test_due_day_crosses_year() -> None:
    """today=Dec 20, due_day=10 → next_due=Jan 10 next year"""
    today = date(2025, 12, 20)
    _, _, next_due = _next_due_date(10, _today=today)
    assert next_due == date(2026, 1, 10)


def test_due_day_clamped_for_short_month() -> None:
    """due_day=31, today=Feb 1 → next_due=Feb 28 (2025 not leap year)"""
    today = date(2025, 2, 1)
    _, _, next_due = _next_due_date(31, _today=today)
    assert next_due == date(2025, 2, 28)


def test_due_day_today_equals_due_day() -> None:
    """today=Mar 15, due_day=15 → next_due=Mar 15 (today is the due day)"""
    today = date(2025, 3, 15)
    period_start, period_end, next_due = _next_due_date(15, _today=today)
    assert next_due == date(2025, 3, 15)
    assert period_start == today
    assert period_end == date(2025, 3, 14)


def test_due_day_clamped_next_month() -> None:
    """today=Jan 31 (past due_day=30) → next month is Feb; 30 > Feb's 28 → Feb 28"""
    today = date(2025, 1, 31)
    _, _, next_due = _next_due_date(30, _today=today)
    assert next_due == date(2025, 2, 28)


def test_advance_on_due_day_advances_to_next_month() -> None:
    """advance=True when today==due_day → next_due must be next month, not today"""
    today = date(2025, 3, 15)
    _, _, next_due = _next_due_date(15, _today=today, advance=True)
    assert next_due == date(2025, 4, 15)


def test_advance_before_due_day_keeps_same_month() -> None:
    """advance=True when today < due_day → next_due still this month"""
    today = date(2025, 3, 5)
    _, _, next_due = _next_due_date(15, _today=today, advance=True)
    assert next_due == date(2025, 3, 15)
