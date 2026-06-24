"""Alembic migration environment configuration."""
from __future__ import annotations
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from app.database import Base
from app.config import config

# this is the Alembic Config object
alembic_config = context.config

# Interpret the config file for Python logging.
if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

# Set SQLAlchemy URL from config
alembic_config.set_main_option("sqlalchemy.url", config.DATABASE_URL)

# Set target metadata for autogeneration
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    
    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well.
    """
    url = alembic_config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    
    In this scenario we need to create an Engine and associate a connection
    with the context.
    """
    configuration = alembic_config.get_section(alembic_config.config_ini_section)
    configuration["sqlalchemy.url"] = config.DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.StaticPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
