"""Alembic Migration Environment Configuration"""
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from dotenv import load_dotenv

# Load the .env file
load_dotenv()


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import Base
from modules.chatbot_agent.model import chatbot_agent
from modules.chatbot.model import chatbot
from modules.chatbot_node.model import chatbot_node
from modules.chatbot_tool.model import chatbot_tool
from modules.chatbot_state.model import chatbot_state
from modules.conversation.model import conversation
from modules.chat_message.model import chat_message


# Import all models to ensure they are registered with Base.metadata
# Add your model imports here as needed
# from modules.user.model import User  # noqa: F401

target_metadata = Base.metadata


print(f"DEBUG: Found tables in metadata: {list(target_metadata.tables.keys())}")

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# def run_migrations_online() -> None:
#     """Run migrations in 'online' mode.

#     In this scenario we need to create an Engine
#     and associate a connection with the context.

#     """
#     connectable = engine_from_config(
#         config.get_section(config.config_ini_section, {}),
#         prefix="sqlalchemy.",
#         poolclass=pool.NullPool,
#     )

#     with connectable.connect() as connection:
#         context.configure(
#             connection=connection, target_metadata=target_metadata
#         )

#         with context.begin_transaction():
#             context.run_migrations()


import asyncio
from sqlalchemy.ext.asyncio import create_async_engine # Ensure this is imported

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    
    # 1. Read the configuration URL
    ini_section = config.get_section(config.config_ini_section, {})
    db_url = ini_section.get("sqlalchemy.url")

    # 2. Build the async engine directly
    connectable = create_async_engine(db_url)

    # 3. Define an inner sync runner function
    def do_run_migrations(connection):
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

    # 4. Define an async runner to establish the connection
    async def run_async():
        async with connectable.connect() as connection:
            # run_sync safely bridges the async connection into the sync migration loop
            await connection.run_sync(do_run_migrations)
        
        await connectable.dispose()

    # 5. Execute the async loop
    asyncio.run(run_async())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
