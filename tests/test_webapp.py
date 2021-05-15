def test_register(client):
    response = client.get('/register')
    assert len(response.data) == 10


def test_operation(client):
    response = client.get(
        '/correcthorsebatterystaple/?action=buy&currency=bigant&amount=100&rate=1.5'
    )
    assert b'{"bigant":100,"usd":850}' in response.data


def test_zero_balance(client):
    responce = client.get(
        '/correcthorsebatterystaple/?action=sell&currency=bigant&amount=100&rate=1.5'
    )
    assert b'{"error":"not enough currency to perform operation"}' in responce.data


def test_unknown_action(client):
    responce = client.get(
        '/correcthorsebatterystaple/?action=transfer&currency=bigant&amount=100&rate=1.5'
    )
    assert b'{"error":"unknown action"}' in responce.data


def test_incorrect_rate(client):
    responce = client.get(
        '/correcthorsebatterystaple/?action=buy&currency=bigant&amount=100&rate=13.37'
    )
    assert b'{"error":"rate is incorrect"}' in responce.data


def test_balance(client):
    response = client.get('/correcthorsebatterystaple/balance')
    assert (
        b'{"bigant":0,"cryptohoney":0,"goldcoin":0,"hopefulite":0,"silverpot":0,"usd":1000}'
        in response.data
    )


def test_rates(client):
    responce = client.get('/rates')
    assert (
        b'{"bigant":1.5,"cryptohoney":3.0,"goldcoin":120.0,"hopefulite":0.5,"silverpot":60.0}'
        in responce.data
    )


def test_history(client):
    client.get(
        '/correcthorsebatterystaple/?action=buy&currency=bigant&amount=100&rate=1.5'
    )
    responce = client.get('/correcthorsebatterystaple/history')
    assert b'{"action":"buy","bigant":100,"usd":-150}' in responce.data


def test_add_currency(client):
    responce = client.get('/add_currency?name=bitcoin&rate=1.0')
    assert b'{"success":"bitcoin was successfully added"}' in responce.data
