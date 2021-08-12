from aiogram.dispatcher.filters.state import State, StatesGroup


class NewReminder(StatesGroup):
    reminder = State()
    time = State()


class Start(StatesGroup):
    tz = State()


class NewPeriodicReminder(StatesGroup):
    reminder = State()
    first_time = State()
    period = State()
