from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError

import app.models  # noqa: F401 — registers all models on Base.metadata
from alembic import context
from app.database import Base  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    from app.config import settings

    return settings.database_url


def ensure_database_exists(url: str) -> None:
    """Create the target database if it does not exist yet.

    Silently skips if the maintenance database is inaccessible (e.g. managed
    cloud Postgres where the database is pre-created by the platform).
    """
    try:
        parsed = make_url(url)
        db_name = parsed.database
        admin_url = parsed.set(database="postgres")
        engine = engine_from_config(
            {"sqlalchemy.url": admin_url.render_as_string(hide_password=False)},
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
        with engine.connect() as conn:
            conn.execute(text("COMMIT"))  # exit any open transaction
            exists = conn.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": db_name},
            )
            if not exists:
                conn.execute(text(f'CREATE DATABASE "{db_name}"'))
        engine.dispose()
    except OperationalError:
        # Maintenance database inaccessible — target database already exists.
        pass


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    ensure_database_exists(get_url())
    run_migrations_online()
