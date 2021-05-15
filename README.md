## Модель API для криптобиржи

Биржа, на которой изначально присутсвует 5 валют.
Можно зарегистрироваться, совершать операции на покупку и продажу валюты, получать курсы, свой баланс и историю своих операций.

Так же можно создать тестовую БД или запустить бота, который будет играть на бирже.

Краткое описание API:

1. `localhost:5000/register` -- регистрация в системе, возвращает токен;
2. `localhost:5000/rates` -- получить имена валют и их курсы;   
3. `localhost:5000/<token>/?action=[buy|sell]&currency=[currency_name]&amount=[amount_value]&rate=[rate_value]` -- совершиить операцию, token - токен, полученный при регистрации, currency - имя валюты, amount количество валюты для операции, rate - курс валюты;
4. `localhost:5000/<token>/balance` -- получить текущий баланс по всем валютам;
5. `localhost:5000/<token>/history` -- получить историю покупок/продаж по вашему токену;
6. `localhost:5000/add_currency?name=[currency_name]&rate=[starting_rate]` -- добавить новую валюту на биржу, нужно указать имя валюты и стартовый курс.

Курс каждой валют меняется на ±1-10% каждые 10 секунд.    

    
### Create venv:
    make venv

### Run tests:
    make test
    
### Run linters:
    make lint
    
### Run formatters:
    make format

### Create SQLite3 database:
    make db

### Run server:
    make up

### Run trade bot: 
    make bot
    