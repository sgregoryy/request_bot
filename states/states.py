from aiogram.fsm.state import State, StatesGroup

class Application(StatesGroup):
    uuid = State()
    date = State()
    time = State()
    ticker = State()
    desc = State()
    image = State()
    twit_link = State()
    tg_link = State()
    website_link = State()
    wallet = State()
    sol_amount = State()
    transaction_hash = State()
    status = State()
    tg_teg = State()

class User(StatesGroup):
    user_id = State()
    uuid = State()

class AdminWallet(StatesGroup):
    wallet = State()