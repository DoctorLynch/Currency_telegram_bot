from enum import Enum


class BotState(Enum):
    START = 0
    AWAITING_AMOUNT = 1
    AWAITING_CURRENCY = 2
    AWAITING_TWO_CURRENCIES = 3

