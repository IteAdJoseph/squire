"""
Worker stub — will be replaced with ARQ-based async worker when jobs are implemented.
Compatible with: python -m app.worker
"""

import asyncio
import logging

from app.config import settings

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(level=settings.log_level)
    logger.info("Worker started (stub — no jobs configured yet)")
    while True:
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
