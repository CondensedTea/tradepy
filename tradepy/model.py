from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    token = Column(String, primary_key=True, unique=True)


class Currency(Base):
    __tablename__ = 'currencies'
    name = Column(String, primary_key=True, unique=True)
    rate = Column(Integer, CheckConstraint('rate > 0'))


class Balance(Base):
    __tablename__ = 'balances'
    id = Column(Integer, primary_key=True, unique=True)
    user_token = Column(String)
    currency = Column(String, ForeignKey('currencies.name'))
    amount = Column(Integer, CheckConstraint('amount >= 0'))


class LogEntry(Base):
    __tablename__ = 'log'
    event_id = Column(Integer, primary_key=True, unique=True)
    user_token = Column(String, ForeignKey('users.token'))
    action = Column(String, CheckConstraint('action == "sell" or action == "buy"'))
    currency = Column(String, ForeignKey('currencies.name'))
    amount_currency = Column(Integer, CheckConstraint('amount_currency != 0'))
    amount_usd = Column(Integer, CheckConstraint('amount_usd != 0'))

    timestamp = Column(DateTime)
