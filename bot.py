import asyncio
import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.storage import FSMContext
from aiogram.types.reply_keyboard import ReplyKeyboardRemove
from aiogram.utils import executor

import config
import langs
import states
from keyboards import DefaulfKeyboard, EditListKeyboard, ListKeyboard, TimeKeyboard
from sqliter import Sqliter

sql = Sqliter()

bot = Bot(config.BOT_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
loop = asyncio.get_event_loop()

MINPERIOD = 5 * 60


class CommandFilter:
    def __init__(self, command):
        self.command = command

    def __call__(self, message: types.Message):
        lang = langs.get_lang(message.from_user.language_code)
        return getattr(lang, self.command) == message.text


@dp.message_handler(commands=["start", "help"])
async def process_start_command(message: types.Message):
    lang = langs.get_lang(message.from_user.language_code)
    await message.answer(lang.START_MESSAGE,
                         reply_markup=DefaulfKeyboard(lang))


@dp.message_handler(CommandFilter("NEW_REMINDER_COMMAND"))
async def process_new_reminder(message: types.Message):
    lang = langs.get_lang(message.from_user.language_code)
    await states.NewReminder.reminder.set()
    await message.answer(lang.WRITE_REMINDER,
                         reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=states.NewReminder.reminder)
async def process_new_reminder_time(message: types.Message, state: FSMContext):
    lang = langs.get_lang(message.from_user.language_code)
    reminder = message.text
    await state.update_data(text=reminder)
    await states.NewReminder.time.set()
    await message.answer(lang.ENTER_TIME, reply_markup=TimeKeyboard(lang))


@dp.message_handler(state=states.NewReminder.time)
async def process_new_reminder_reminder(message: types.Message,
                                        state: FSMContext):
    lang = langs.get_lang(message.from_user.language_code)
    t = lang.parse_time(message.text)
    if not t:
        await message.answer(lang.ERROR_PARSE_TIME)
        return
    async with state.proxy() as data:
        sql.insert_reminder(
            dict(user_id=message.from_user.id,
                 text=data["text"],
                 time=t,
                 period=0))
        await message.answer(
            lang.REMINDER_WRITED.format(datetime.datetime.fromtimestamp(t)),
            reply_markup=DefaulfKeyboard(lang),
        )
    await state.finish()


@dp.message_handler(CommandFilter("NEW_PERIODIC_REMINDER_COMMAND"))
async def process_new_periodic_reminder(message: types.Message):
    lang = langs.get_lang(message.from_user.language_code)
    await states.NewPeriodicReminder.reminder.set()
    await message.answer(lang.WRITE_REMINDER,
                         reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=states.NewPeriodicReminder.reminder)
async def process_new_periodic_reminder_reminder(message: types.Message,
                                                 state: FSMContext):
    lang = langs.get_lang(message.from_user.language_code)
    reminder = message.text
    await state.update_data(text=reminder)
    await message.answer(lang.ENTER_FIRST_TIME,
                         reply_markup=TimeKeyboard(lang))
    await states.NewPeriodicReminder.first_time.set()


@dp.message_handler(state=states.NewPeriodicReminder.first_time)
async def process_new_periodic_reminder_first_time(message: types.Message,
                                                   state: FSMContext):
    lang = langs.get_lang(message.from_user.language_code)
    first_time = lang.parse_time(message.text)
    if not first_time:
        await message.answer(lang.ERROR_PARSE_TIME)
        return
    await state.update_data(first_time=first_time)
    await message.answer(lang.ENTER_PERIOD, reply_markup=TimeKeyboard(lang))
    await states.NewPeriodicReminder.period.set()


@dp.message_handler(state=states.NewPeriodicReminder.period)
async def process_new_periodic_reminder_period(message: types.Message,
                                               state: FSMContext):
    lang = langs.get_lang(message.from_user.language_code)
    period = lang.parse_time(message.text)
    if not period:
        await message.answer(lang.ERROR_PARSE_TIME)
        return
    period = abs(period - lang.parse_time("now"))
    if period < MINPERIOD:
        await message.answer(lang.TOO_SHORT_PERIOD)
        return
    async with state.proxy() as data:
        sql.insert_reminder(
            dict(
                user_id=message.from_user.id,
                text=data["text"],
                time=data["first_time"],
                period=period,
            ))
        await message.answer(lang.SAVED, reply_markup=DefaulfKeyboard(lang))
    await state.finish()


def build_list(reminders, start, lang):
    text = lang.YOUR_LIST if reminders else lang.YOUR_LIST_EMPTY
    for rem in enumerate(reminders[start:start + 8], start + 1):
        if not rem[1]["period"]:
            x_text = (rem[1]["text"] if len(rem[1]["text"]) <= 40 else
                      rem[1]["text"][:40] + "...")
            text += lang.ID_LIST_ITEM.format(
                id=rem[0],
                time=datetime.datetime.fromtimestamp(rem[1]["time"]),
                text=x_text,
            )
        else:
            text += lang.PERIOD_LIST_ITEM.format(
                id=rem[0],
                time=datetime.datetime.fromtimestamp(rem[1]["time"]),
                text=rem[1]["text"],
                period=lang.timeformat(rem[1]["period"]),
            )
    return text


@dp.message_handler(CommandFilter("SHOW_LIST"))
async def process_show_list_command(message: types.Message):
    lang = langs.get_lang(message.from_user.language_code)
    reminders = sql.select_by_user(message.from_user.id)
    text = build_list(reminders, 0, lang)
    keyboard = ListKeyboard(1, len(reminders), 0, len(reminders) > 8, lang)
    await message.answer(text, reply_markup=keyboard)


@dp.callback_query_handler(
    lambda q: q.data and q.data.startswith("list-change-page"))
async def process_list_callbacks(callback_query: types.CallbackQuery):
    lang = langs.get_lang(callback_query.from_user.language_code)
    reminders = sql.select_by_user(callback_query.from_user.id)
    way, ind = callback_query.data.split("-")[-2:]
    ind = int(ind) - 1
    if way == "next":
        ind += 8
    else:
        ind -= 8
    text = build_list(reminders, ind, lang)
    keyboard = ListKeyboard(ind + 1, min(ind + 9, len(reminders)), ind > 0,
                            len(reminders) > ind + 8, lang)
    await callback_query.message.edit_text(text)
    if text != lang.YOUR_LIST_EMPTY:
        await callback_query.message.edit_reply_markup(keyboard)


@dp.callback_query_handler(
    lambda q: q.data and q.data.startswith("list-item-menu"))
async def process_list_item_menu(callback_query: types.CallbackQuery):
    lang = langs.get_lang(callback_query.from_user.id)
    index = int(callback_query.data.split("-")[-1])
    reminders = sql.select_by_user(callback_query.from_user.id)
    if index > len(reminders):
        callback_query.data = "list-change-page-prev-9"
        await process_list_callbacks(callback_query)
        return
    await callback_query.message.edit_text(
        lang.LIST_ITEM.format(
            time=datetime.datetime.fromtimestamp(reminders[index - 1]["time"]),
            text=reminders[index - 1]["text"],
        ))
    await callback_query.message.edit_reply_markup(
        EditListKeyboard(index, lang))


@dp.callback_query_handler(
    lambda q: q.data and q.data.startswith("list-item-delete"))
async def process_list_item_delete(callback_query: types.CallbackQuery):
    index = int(callback_query.data.split("-")[-1]) - 1
    reminders = sql.select_by_user(callback_query.from_user.id)
    if index < len(reminders):
        sql.delete(reminders[index]["id"])
    callback_query.data = "list-change-page-prev-9"
    await process_list_callbacks(callback_query)


@dp.message_handler()
async def process_all(message: types.Message):
    lang = langs.get_lang(message.from_user.id)
    await message.answer(lang.WRONG_INPUT)


async def check_tasks():
    for task in sql.select_good():
        await bot.send_message(task["user_id"], text=task["text"])


def repeat_check_tasks(loop):
    asyncio.ensure_future(check_tasks(), loop=loop)
    loop.call_later(2, repeat_check_tasks, loop)


if __name__ == "__main__":
    loop.call_later(2, repeat_check_tasks, loop)
    executor.start_polling(dp, loop=loop)
