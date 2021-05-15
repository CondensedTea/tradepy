import random
import string
from contextlib import contextmanager
from datetime import datetime
from http import HTTPStatus
from typing import Any, Dict, Iterator, List, Optional, Tuple

from flask import Blueprint, current_app, request
from sqlalchemy.orm import Query, Session

from tradepy.model import Balance, Currency, LogEntry, User

tradepy_app = Blueprint('tradepy_app', __name__)


@contextmanager
def create_session(s: Session) -> Iterator[Session]:
    new_session = s
    try:
        yield new_session
        new_session.commit()
    except Exception:
        new_session.rollback()
        raise
    finally:
        new_session.close()


def calculate_currency_diff(
    action_multiplier: int, user_rate: float, amount: int
) -> Tuple[int, int]:
    deal_price_usd: int = int(amount * (user_rate / 100) * -action_multiplier)
    deal_price_currency: int = amount * action_multiplier
    return deal_price_usd, deal_price_currency


@tradepy_app.route('/register')
def register() -> Tuple[str, int]:
    alphanumeric: str = string.ascii_letters + string.digits
    token = ''.join(random.choice(alphanumeric) for i in range(10))
    with create_session(current_app.config['SESSION']()) as session:
        currencies: List[Currency] = session.query(Currency).all()
        for c in currencies:
            session.add(Balance(user_token=token, currency=c.name, amount=0))
        session.add(Balance(user_token=token, currency='usd', amount=1000))
        session.add(User(token=token))
        return token, HTTPStatus.OK


@tradepy_app.route('/<token>/')
def operation(token: str) -> Tuple[Dict[str, Any], int]:
    action: Optional[str] = request.args.get('action', type=str)
    user_currency: Optional[str] = request.args.get('currency', type=str)
    amount: Optional[int] = request.args.get('amount', type=int)
    rate_dollars: Optional[float] = request.args.get('rate', type=float)
    if not action or not user_currency or not amount or not rate_dollars:
        return {'error': 'not enough arguments'}, HTTPStatus.PRECONDITION_REQUIRED
    rate: int = int(rate_dollars * 100)
    with create_session(current_app.config['SESSION']()) as session:
        currency: Currency = (
            session.query(Currency).filter(Currency.name == user_currency).one()
        )
        if action == 'buy':
            action_multiplier = 1
        elif action == 'sell':
            action_multiplier = -1
        else:
            return {'error': 'unknown action'}, HTTPStatus.NOT_ACCEPTABLE
        if currency.rate != rate:
            return {'error': 'rate is incorrect'}, HTTPStatus.CONFLICT
        balance_currency: Balance = (
            session.query(Balance)
            .filter(Balance.user_token == token, Balance.currency == currency.name)
            .one()
        )
        balance_usd: Balance = (
            session.query(Balance)
            .filter(Balance.user_token == token, Balance.currency == 'usd')
            .one()
        )
        if balance_usd.amount is None or balance_currency.amount is None:
            return {'error': 'cannot get your balance' + user_currency}, 403
        deal_usd, deal_currency = calculate_currency_diff(
            action_multiplier, rate, amount
        )
        if (
            balance_usd.amount + deal_usd < 0
            or balance_currency.amount + deal_currency < 0
        ):
            return {'error': 'not enough currency to perform operation'}, 403
        balance_usd.amount += deal_usd
        balance_currency.amount += deal_currency
        session.add(
            LogEntry(
                user_token=token,
                currency=currency.name,
                action=action,
                amount_currency=deal_currency,
                amount_usd=deal_usd,
                timestamp=datetime.now(),
            )
        )
        return {
            'usd': balance_usd.amount,
            currency.name: balance_currency.amount,
        }, HTTPStatus.OK


@tradepy_app.route('/<token>/balance')
def balance(token: str) -> Tuple[Dict[str, int], int]:
    response: Dict[str, int] = {}
    with create_session(current_app.config['SESSION']()) as session:
        balances_list: List[Balance] = (
            session.query(Balance).filter(Balance.user_token == token).all()
        )
        for b in balances_list:
            if b.currency is not None and b.amount is not None:
                response[b.currency] = b.amount
        return response, HTTPStatus.OK


@tradepy_app.route('/rates')
def rates() -> Tuple[Dict[str, float], int]:
    response: Dict[str, float] = {}
    with create_session(current_app.config['SESSION']()) as session:
        rates_list: List[Currency] = session.query(Currency).all()
        for r in rates_list:
            if r.name is not None and r.rate is not None:
                response[r.name] = r.rate / 100
        return response, HTTPStatus.OK


@tradepy_app.route('/<token>/history')
def history(token: str) -> Tuple[Dict[str, Dict[str, str]], int]:
    start: Optional[int] = request.args.get('start', default=1, type=int) - 1
    stop: Optional[int] = request.args.get('stop', default=5, type=int)
    response: Dict[str, Dict[str, Any]] = {}
    with create_session(current_app.config['SESSION']()) as session:
        log: Query[LogEntry] = (
            session.query(LogEntry)
            .filter(LogEntry.user_token == token)
            .slice(start, stop)
        )
        for entry in log:
            if (
                entry.timestamp
                and entry.action
                and entry.amount_usd
                and entry.currency
                and entry.amount_currency
            ):
                response[entry.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')] = {
                    'action': entry.action,
                    'usd': entry.amount_usd,
                    entry.currency: entry.amount_currency,
                }
        return response, HTTPStatus.OK


@tradepy_app.route('/add_currency')
def add_currency() -> Tuple[Dict[str, str], int]:
    name: Optional[str] = request.args.get('name', type=str)
    rate_dollars: Optional[float] = request.args.get('rate', type=float)
    if rate_dollars and name:
        rate: int = int(rate_dollars * 100)
        with create_session(current_app.config['SESSION']()) as session:
            for user in session.query(User).all():
                session.add(Balance(user_token=user.token, currency=name, amount=0))
            session.add(Currency(name=name, rate=rate))
        return {'success': name + ' was successfully added'}, HTTPStatus.ACCEPTED
    return {'error': 'not enough arguments'}, HTTPStatus.PRECONDITION_REQUIRED
