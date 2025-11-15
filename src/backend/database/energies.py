import os

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database


def get_engine():
    db_url = (
        "postgresql://"
        f"{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:"
        f"{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}"
    )

    if not database_exists(db_url):
        create_database(db_url)

    engine = create_engine(db_url, pool_size=50, echo=False)
    return engine
