from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# adiciona o diretório base ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db

# cria a aplicação Flask sem empurrar contexto manualmente
flask_app = create_app()

# configura o Alembic
config = context.config
fileConfig(config.config_file_name)

# define a metadata para autogeração
target_metadata = db.metadata

def run_migrations_offline():
    """Executa as migrações em modo offline (sem conexão ativa)."""
    url = flask_app.config['SQLALCHEMY_DATABASE_URI']
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Executa as migrações em modo online (com conexão ativa)."""
    connectable = db.engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

