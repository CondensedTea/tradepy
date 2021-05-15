from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from tradepy.webapp import tradepy_app

database_file = 'sqlite:///tradepy/tradepy.sqlite3'


def create_app(engine: Engine = create_engine(database_file, echo=True)) -> Flask:
    app = Flask(__name__)
    app.register_blueprint(tradepy_app)
    app.config['SESSION'] = sessionmaker(bind=engine)
    return app
