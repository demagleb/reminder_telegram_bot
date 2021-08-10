from aiogram.types import ReplyKeyboardMarkup, \
    InlineKeyboardMarkup, InlineKeyboardButton
import langs


class DefaulfKeyboard(ReplyKeyboardMarkup):
    def __init__(self, lang: langs.Russian):
        super().__init__(resize_keyboard=True)
        self.row(lang.SHOW_LIST).row(lang.NEW_REMINDER_COMMAND,
                                     lang.NEW_PERIODIC_REMINDER_COMMAND)


class TimeKeyboard(ReplyKeyboardMarkup):
    def __init__(self, lang: langs.Russian):
        super().__init__(resize_keyboard=True, one_time_keyboard=True)
        self.add(lang.TimePediods.MIN10,
                 lang.TimePediods.MIN30, lang.TimePediods.HOUR1,
                 lang.TimePediods.HOUR5, lang.TimePediods.DAY1)


class ListKeyboard(InlineKeyboardMarkup):
    def __init__(self, start: int, end: int, has_prev: bool, has_next: bool, lang: langs.Russian):
        super().__init__()
        self.row(*[InlineKeyboardButton(str(i), callback_data='list-item-menu-{}'.format(i))
                   for i in range(start, end + 1)])
        prevnext = []
        if has_prev:
            prevnext.append(InlineKeyboardButton(
                lang.PREVIOUS, callback_data='list-change-page-prev-{}'.format(start)))
        if has_next:
            prevnext.append(InlineKeyboardButton(
                lang.NEXT, callback_data='list-change-page-next-{}'.format(start)))
        self.row(*prevnext)


class EditListKeyboard(InlineKeyboardMarkup):
    def __init__(self, index: int, lang: langs.Russian):
        super().__init__()
        self.row(InlineKeyboardButton(
            lang.DELETE, callback_data='list-item-delete-{}'.format(index)))
