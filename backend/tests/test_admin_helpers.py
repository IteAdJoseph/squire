from datetime import date

from app.admin.router import _advance_billing_cycle, _next_due_date


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


# ---------------------------------------------------------------------------
# _advance_billing_cycle — avança 1 mês a partir do due date atual
# Independente de quando o pagamento chegou (antes, no dia, depois).
# ---------------------------------------------------------------------------


def test_advance_payment_early() -> None:
    """Pagamento adiantado (Mar 10): ciclo avança Mar 15 → Apr 15."""
    current_due = date(2025, 3, 15)
    payment_date = date(2025, 3, 10)
    period_start, period_end, next_due = _advance_billing_cycle(
        current_due, 15, _today=payment_date
    )
    assert next_due == date(2025, 4, 15)
    assert period_start == payment_date
    assert period_end == date(2025, 4, 14)


def test_advance_payment_on_due_day() -> None:
    """Pagamento no dia (Mar 15): ciclo avança Mar 15 → Apr 15."""
    current_due = date(2025, 3, 15)
    payment_date = date(2025, 3, 15)
    period_start, period_end, next_due = _advance_billing_cycle(
        current_due, 15, _today=payment_date
    )
    assert next_due == date(2025, 4, 15)
    assert period_start == payment_date
    assert period_end == date(2025, 4, 14)


def test_advance_payment_late() -> None:
    """Pagamento atrasado (Mar 20): ciclo avança Mar 15 → Apr 15."""
    current_due = date(2025, 3, 15)
    payment_date = date(2025, 3, 20)
    period_start, period_end, next_due = _advance_billing_cycle(
        current_due, 15, _today=payment_date
    )
    assert next_due == date(2025, 4, 15)
    assert period_start == payment_date
    assert period_end == date(2025, 4, 14)


def test_advance_crosses_year() -> None:
    """Ciclo Dec 15 avança para Jan 15 do ano seguinte."""
    current_due = date(2025, 12, 15)
    payment_date = date(2025, 12, 20)
    _, _, next_due = _advance_billing_cycle(current_due, 15, _today=payment_date)
    assert next_due == date(2026, 1, 15)


def test_advance_clamps_for_short_month() -> None:
    """Ciclo Jan 31 (due_day=31) avança para Feb 28 (fevereiro tem 28 dias)."""
    current_due = date(2025, 1, 31)
    payment_date = date(2025, 1, 31)
    _, _, next_due = _advance_billing_cycle(current_due, 31, _today=payment_date)
    assert next_due == date(2025, 2, 28)


def test_advance_very_late_payment() -> None:
    """Pagamento muito atrasado: current_due=Feb 15, pagamento em Mar 20.

    Feb→Mar (Mar 15 ≤ Mar 20) → avança mais um mês → Apr 15 > Mar 20. Correto.
    Garante que period_end >= period_start (período nunca invertido).
    """
    current_due = date(2025, 2, 15)
    payment_date = date(2025, 3, 20)
    period_start, period_end, next_due = _advance_billing_cycle(
        current_due, 15, _today=payment_date
    )
    assert next_due == date(2025, 4, 15)
    assert period_start == payment_date
    assert period_end == date(2025, 4, 14)
    assert period_end >= period_start
