"""
Scheduler stub — executes every 5 min via Render cron (reminda-scheduler).
Compatible with: python -m app.jobs.run_due

Responsibilities (to be implemented):
  1. Check billing_accounts with overdue next_due_date and update status.
  2. Enqueue pending Reminders with scheduled_for <= now for the worker.
"""

import logging

from app.config import settings

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=settings.log_level)
    logger.info("run_due started (stub — no jobs configured yet)")


if __name__ == "__main__":
    main()
