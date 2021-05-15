import pytest
import responses
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tools.create_db import data, token
from tradepy import create_app
from tradepy.model import Balance, Base, Currency


@pytest.fixture(name='tmp_database_engine')
def fixture_tmp_database_engine(tmp_path):
    path = tmp_path / 'test_database.sqlite'
    engine = create_engine('sqlite:////' + str(path))
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    path.unlink()


@pytest.fixture(autouse=True)
def create_data(tmp_database_engine):
    Session = sessionmaker(tmp_database_engine)
    session = Session()
    session.bulk_save_objects(data)
    for c in session.query(Currency).all():
        session.add(Balance(user_token=token, currency=c.name, amount=0))
    session.commit()
    session.close()


@pytest.fixture()
def client(tmp_database_engine):
    app = create_app(tmp_database_engine)
    with app.app_context():
        with app.test_client():
            return app.test_client()


@pytest.fixture()
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps
