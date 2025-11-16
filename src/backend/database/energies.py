import os

import requests
from sqlalchemy import create_engine, Column, String, Integer, inspect
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()


class Symbol(Base):
    __tablename__ = "symbols"

    symbol = Column(String(100), primary_key=True)
    category = Column(String(100), nullable=False)
    currency = Column(JSONB(), nullable=False)
    unit = Column(JSONB(), nullable=False)
    name = Column(String(100))
    status = Column(String(100))
    updateInterval = Column(String(100))


def __get_engine():
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


def __create_tables(engine) -> bool:
    insp = inspect(engine)
    if insp == []:
        Base.metadata.create_all(engine)
        return True
    return False


def __query(endpoint: str, **kwargs) -> dict:
    base_url = (
        f"https://api.commoditypriceapi.com/v2{endpoint}?"
        f"apiKey={os.getenv('API_KEY')}"
    )
    for arg, val in kwargs.items():
        base_url += f"&{arg}={val}"

    response = requests.get(base_url)
    if response.status_code != 200:
        return {}
    return response.json()


def __get_base_data_from_api(engine) -> None:
    symbols = __query("/symbols")
    if symbols == {}:
        return

    session = sessionmaker(bind=engine)()
    
    for symbol in symbols["symbols"]:
        if symbol["category"] != "Energy":
            continue
        session.add(Symbol(
            symbol=symbol["symbol"],
            category=symbol["category"],
            currency=symbol["currency"],
            unit=symbol["unit"],
            name=symbol["name"],
            status=symbol["status"],
            updateInterval=symbol["updateInterval"]
        ))
    session.flush()
    session.commit()


def init_database() -> None:
    engine = __get_engine()
    is_created = __create_tables(engine)
    if is_created:
        __get_base_data_from_api(engine)


def get_energies() -> list[Symbol]:
    engine = __get_engine()
    session = sessionmaker(bind=engine)()
    return session.query(Symbol).all()
