from telebot import types
from currency_converter import CurrencyConverter
from my_bot import bot
from bot_logger import BotLogger

logger = BotLogger('bot.log')

currency = CurrencyConverter()
amount = 0


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == "/start":
        bot.send_message(message.chat.id, 'Вас приветствует конвертер валюты, '
                                          'для того чтобы начать введите /convert')
        bot.register_next_step_handler(message, convert)
    elif message.text == "/help":
        bot.send_message(message.chat.id, 'Введите /start для приветствия или /convert чтобы сразу начать')
    else:
        bot.send_message(message.chat.id, 'Я тебя не понимаю. Напиши /help.')


@bot.message_handler(content_types=['text'])
def convert(message):
    if message.text == "/convert":
        bot.send_message(message.chat.id, 'Пожалуйста введите число для конвертации')
        bot.register_next_step_handler(message, summa)
    else:
        bot.send_message(message.chat.id, 'Я тебя не понимаю. Напиши /help.')


def summa(message):
    global amount
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Неверно, введите число без запятых.')
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
    if call.data != 'else':
        values = call.data.upper().split('/')
        result = round(currency.convert(amount, values[0], values[1]), 2)
        bot.send_message(call.message.chat.id, f'Итог конвертации: {result}. Можно ввести сумму ещё раз')
        bot.register_next_step_handler(call.message, summa)
    else:
        bot.send_message(call.message.chat.id, 'Введите 2 значения через слэш')
        bot.register_next_step_handler(call.message, my_currency)


def my_currency(message):
    try:
        values = message.text.upper().split('/')
        result = round(currency.convert(amount, values[0], values[1]), 2)
        bot.send_message(message.chat.id, f'Итог конвертации: {result}. Можно ввести сумму ещё раз')
        bot.register_next_step_handler(message, summa)
    except Exception:
        bot.send_message(message.chat.id, 'Некорректный формат, попробуйте ещё раз')
        bot.register_next_step_handler(message, my_currency)


bot.polling(none_stop=True)

# if __name__ == '__main__':
#     pass
