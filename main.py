from telebot import types
from currency_converter import CurrencyConverter

from bot_status import BotState
from my_bot import bot
from bot_logger import BotLogger

logger = BotLogger('bot.log')  # Создаём экземпляр класса для логирования

currency = CurrencyConverter()
amount = 0

greeting = ['привет', 'здравствуйте', 'hello']
goodbye = ['до свидания', 'пока', 'bye']

current_state = BotState.START


@bot.message_handler(commands=['start'])
def start_handler(message):
    """
            Функция обрабатывает команду старт от пользователя, также не забывая о том
            что русскому человеку нужно обязательно повторить
    """
    global current_state
    current_state = BotState.START
    if message.text == "/start":
        user_id = message.from_user.id
        logger.log_info(f"Пользователь {user_id} запустил бота с командой /start")
        bot.send_message(message.chat.id, "Добро пожаловать! "
                                          "Это бот для конвертации валюты, для начала"
                                          "введите команду '/convert")
        bot.register_next_step_handler(message, convert_help_handler)


@bot.message_handler(commands=['help', 'convert'])
def convert_help_handler(message):
    """
        Функция обрабатывает команды конверт и help от пользователя
    """
    global current_state
    current_state = BotState.START
    if message.text == "/help":
        keyboard = types.InlineKeyboardMarkup()
        convert_button = types.InlineKeyboardButton(text='Конвертировать', callback_data='convert')
        cancel_button = types.InlineKeyboardButton(text='Завершить', callback_data='exit')
        keyboard.row(convert_button, cancel_button)
        bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=keyboard)
    elif message.text == "/convert":
        bot.send_message(message.chat.id, "Введите число для конвертации")
        bot.register_next_step_handler(message, convert_summa)
    else:
        bot.send_message(message.chat.id, 'Я тебя не понимаю. Напиши /help.')
        bot.register_next_step_handler(message, convert_help_handler)


@bot.message_handler()
def first_look(message):
    """
    Функция принимает на вход сообщение от пользователя и
    в зависимости от текста выводит ответ
    """
    global current_state
    current_state = BotState.START
    if message.text.lower() in greeting:
        bot.send_message(message.chat.id, 'Привет')
    elif message.text.lower() in goodbye:
        bot.send_message(message.chat.id, 'Всего хорошего, удачного курса Вам')
        bot.stop_bot()
    else:
        bot.send_message(message.chat.id, 'Для начала введите /start')


@bot.callback_query_handler(func=lambda call: call.data == 'convert')
def handle_convert_callback(call):
    """
        Функция принимает число для конвертации валюты
    """
    global current_state
    current_state = BotState.AWAITING_AMOUNT
    bot.send_message(call.message.chat.id, "Введите число для конвертации")
    bot.register_next_step_handler(call.message, convert_summa)


@bot.callback_query_handler(func=lambda call: call.data == 'exit')
def handle_cancel_callback(call):
    """
        Функция обрабатывает кнопку команду "exit" при нажатии кнопки "Завершить"
    """
    global current_state
    current_state = BotState.START
    bot.send_message(call.message.chat.id, 'Завершение работы конвертера. Всего хорошего)')
    bot.stop_bot()


def convert_summa(message):
    """
       Функция обрабатывает конвертируемое число и если что-то не так, выводит пользователю подробную инструкцию
    """
    global amount
    global current_state
    current_state = BotState.AWAITING_AMOUNT
    try:
        amount = int(message.text.strip())
    except ValueError as e:
        logger.log_error(f"Ошибка: {str(e)}")
        bot.send_message(message.chat.id, 'Неверно, введите целое число.')
        bot.register_next_step_handler(message, convert_summa)
        return

    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton('EUR/USD', callback_data='eur/usd')
        btn2 = types.InlineKeyboardButton('USD/EUR', callback_data='usd/eur')
        btn3 = types.InlineKeyboardButton('USD/GPB', callback_data='usd/gbp')
        btn4 = types.InlineKeyboardButton('Другие валюты', callback_data='else')
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, 'Выберите валюты(каждая кнопка одноразовая)', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Введите положительное число')
        bot.register_next_step_handler(message, convert_summa)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    """
        Функция, выводящая конвертируемое значение на экран бота
    """
    global current_state
    current_state = BotState.AWAITING_CURRENCY
    if call.data != 'else':
        values = call.data.upper().split('/')
        result = currency.convert(amount, values[0], values[1])
        bot.send_message(call.message.chat.id, f'Итог конвертации: {round(result, 2)}. Выберите другую валюту '
                                               f'или введите новое число')
    else:
        bot.send_message(call.message.chat.id, 'Введите 2 значения через слэш')
        bot.register_next_step_handler(call.message, my_currency)


def my_currency(message):
    """
        Функция, позволяющая пользователю ввести свои валюты, а не только те,
        что представлены в меню
    """
    global current_state
    current_state = BotState.AWAITING_TWO_CURRENCIES
    try:
        values = message.text.upper().split('/')
        result = currency.convert(amount, values[0], values[1])
        bot.send_message(message.chat.id, f'Итог конвертации: {round(result, 2)}. Выберите другую валюту '
                                          f'или введите новое число')
        bot.register_next_step_handler(message, convert_summa)
    except IndexError:
        bot.send_message(message.chat.id, 'Некорректный формат, попробуйте ещё раз')
        bot.register_next_step_handler(message, my_currency)


if __name__ == '__main__':
    bot.polling()  # для постоянной работы бота