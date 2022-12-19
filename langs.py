import dateparser


def dhms(sec: int) -> str:
    d = sec // (24 * 3600)
    h = (sec % (24 * 3600)) // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return d, h, m, s


class Russian:
    @staticmethod
    def parse_time(s: str) -> int:
        x = dateparser.parse(s)
        if x:
            return int(x.timestamp())
        else:
            return None

    def timeformat(sec: int) -> str:
        d, h, m, s = dhms(sec)
        res = ""
        if d:
            res += f"{d} дней"
        if h or d:
            res += f" {h} часов"
        if m or h or d:
            res += f" {m} минут"
        res += f" {s} секунд"
        return res

    START_MESSAGE = "Привет я умею напоминать"
    NEW_REMINDER_COMMAND = "Новое напонимание"
    NEW_PERIODIC_REMINDER_COMMAND = "Новое периодическое напоминание"
    ERROR_PARSE_TIME = "Не удалось определить время((("
    ENTER_TIME = "Введите время"
    ENTER_FIRST_TIME = "Введите время первого напоминания"
    ENTER_PERIOD = "Введите через какое время повторять"
    WRITE_REMINDER = "Напишите свое напоминание"
    REMINDER_WRITED = "Напоминание сохранено на время {}"
    SAVED = "Сохранено"
    SHOW_LIST = "Список напоминаний"
    ID_LIST_ITEM = "{id}) {time} - \n {text}\n"
    YOUR_LIST = "Ваш список напоминаний:\n"
    YOUR_LIST_EMPTY = "Ваш список напоминаний пуст"
    LIST_ITEM = "Ваше напоминание на {time}:\n\n{text}"
    WRONG_INDEX = "Неправельный индекс"
    TOO_SHORT_PERIOD = "Слишком маленький период минимум через 5 минут"
    PERIOD_LIST_ITEM = "{id}) {time} повторять через {period} -\n {text}\n"
    PREVIOUS = "Назад"
    WRONG_INPUT = "Неизвестная команда, нажмите /help"
    NEXT = "Далее"
    EDIT = "Редактировать"
    DELETE = "Удалить"

    class TimePediods:
        MIN10 = "Через 10 минут"
        MIN30 = "Через 30 минут"
        HOUR1 = "Через 1 час"
        HOUR5 = "Через 5 часов"
        DAY1 = "Через день"


def get_lang(lang_code):
    return Russian


if __name__ == "__main__":
    x = Russian
