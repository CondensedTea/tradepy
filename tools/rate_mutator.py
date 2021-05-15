import random
import time
from typing import List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from tools.create_db import sqlite_file
from tradepy.model import Currency

engine = create_engine(sqlite_file, echo=False)
S = sessionmaker(engine)
session = S()


def get_pool(rate: int) -> List[int]:
    if rate in range(1, 100):
        return list(range(101, 111))
    return list(range(101, 111)) + list(range(90, 100))


def mutate_all_currencies(
    s: Session = session, limit: Optional[int] = None, timer: int = 10
) -> None:
    if limit:
        stop: Optional[int] = limit
    else:
        stop = None
    counter = 0
    while True:
        if stop and counter == stop:
            break
        time.sleep(timer)
        currencies = s.query(Currency).all()
        for c in currencies:
            if c.rate:
                pool = get_pool(c.rate)
                delta = random.choice(pool)
                c.rate = int(c.rate * (delta / 100))
                s.commit()
        counter += 1


if __name__ == '__main__':
    mutate_all_currencies()
