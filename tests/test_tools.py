from sqlalchemy.orm import Session

from tools.rate_mutator import mutate_all_currencies
from tradepy.model import Currency
from tradepy.webapp import create_session


def test_rate_mutator(tmp_database_engine):
    s = Session(tmp_database_engine)
    with create_session(s) as session:
        mutate_all_currencies(s=session, limit=2, timer=0)
        mutated_rate = session.query(Currency).filter(Currency.name == 'bigant').one()
        assert mutated_rate != 150
