from telebot import types
from currency_converter import CurrencyConverter
from my_bot import bot
from bot_logger import BotLogger

logger = BotLogger('bot.log') # Создаём экземляр класса для логирования

currency = CurrencyConverter()
amount = 0


@bot.message_handler()
def first_look(message):
    """
    Функция принимает на вход сообщение от пользователя и
    в зависимости от текста выводит ответ
    """
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет')
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'До свидания')
        bot.stop_bot()
    elif message.text == '/help':
        bot.send_message(message.chat.id, '/start - начать использование бота')
        bot.register_next_step_handler(message, start)
    else:
        bot.send_message(message.chat.id, 'Для приветствия введите /start')
        bot.register_next_step_handler(message, start)


@bot.message_handler(content_types=['start'])
def start(message):
    """
        Функция обрабатывает команду старт от пользователя, также незабывая о том
        что русскому человеку нужно обязательно повторить
    """
    if message.text == "/start":
        user_id = message.from_user.id
        logger.log_info(f"Пользователь {user_id} запустил бота с командой /start")
        bot.send_message(message.chat.id, "Добро пожаловать в нашего бота!"
                                          "Чтобы начать введите /convert")
        bot.register_next_step_handler(message, convert)
    elif message.text == '/help':
        bot.send_message(message.chat.id, '/start - начать использование бота')
        bot.register_next_step_handler(message, start)
    else:
        bot.send_message(message.chat.id, 'Я тебя не понимаю. Напиши /help.')


@bot.message_handler(content_types=['text'])
def convert(message):
    """
        Функция принимает число для конвертации одной валюты в другую
    """
    if message.text == "/convert":
        bot.send_message(message.chat.id, 'Пожалуйста введите число для конвертации')
        bot.register_next_step_handler(message, summa)
    else:
        bot.send_message(message.chat.id, 'Я тебя не понимаю. Напиши /help.')


def summa(message):
    """
        Функция обрабатывает конвертируемое число и если что-то не так,
        выводит пользователю подробную инструкцию
    """
    global amount
    try:
        amount = int(message.text.strip())
    except ValueError as e:
        logger.log_error(f"Ошибка: {str(e)}")
        bot.send_message(message.chat.id, 'Неверно, введите целое число.')
        bot.register_next_step_handler(message, summa)
        return

    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton('EUR/USD', callback_data='eur/usd')
        btn2 = types.InlineKeyboardButton('USD/EUR', callback_data='usd/eur')
        btn3 = types.InlineKeyboardButton('USD/GPB', callback_data='usd/gbp')
        btn4 = types.InlineKeyboardButton('Другие валюты', callback_data='else')
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, 'Выберите валюты', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Введите положительное число')
        bot.register_next_step_handler(message, summa)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    """
        Функция, выводящая конвертируемое значение на экран бота
    """
    if call.data != 'else':
        values = call.data.upper().split('/')
        result = round(currency.convert(amount, values[0], values[1]), 2)
        bot.send_message(call.message.chat.id, f'Итог конвертации: {result}. Можно ввести сумму ещё раз')
        bot.register_next_step_handler(call.message, summa)
    else:
        bot.send_message(call.message.chat.id, 'Введите 2 значения через слэш')
        bot.register_next_step_handler(call.message, my_currency)


def my_currency(message):
    """
        Функция, позволяющая пользователю ввести свои валюты, а не только те,
        что представлены в меню
    """
    try:
        values = message.text.upper().split('/')
        result = round(currency.convert(amount, values[0], values[1]), 2)
        bot.send_message(message.chat.id, f'Итог конвертации: {result}. Можно ввести сумму ещё раз')
        bot.register_next_step_handler(message, summa)
    except Exception:
        bot.send_message(message.chat.id, 'Некорректный формат, попробуйте ещё раз')
        bot.register_next_step_handler(message, my_currency)


if __name__ == '__main__':
    bot.polling(none_stop=True) # для постоянной работы бота