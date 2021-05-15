from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from tradepy.model import Balance, Base, Currency, User

token = 'correcthorsebatterystaple'
sqlite_file = 'sqlite:///tradepy/tradepy.sqlite3'


data = [
    Currency(name='goldcoin', rate=12000),
    Currency(name='silverpot', rate=6000),
    Currency(name='cryptohoney', rate=300),
    Currency(name='bigant', rate=150),
    Currency(name='hopefulite', rate=50),
    User(token=token),
    Balance(user_token=token, currency='usd', amount=1000),
]


def create_db(f: str = sqlite_file) -> Engine:
    e = create_engine(f, echo=False)
    Base.metadata.create_all(e)
    return e


def insert_data(engine: Engine) -> None:
    Session = sessionmaker(engine)
    session = Session()
    session.add_all(data)
    for c in session.query(Currency).all():
        session.add(Balance(user_token=token, currency=c.name, amount=0))
    session.commit()


if __name__ == '__main__':
    eng = create_db(sqlite_file)
    insert_data(eng)
