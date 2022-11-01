import enum

# Using enum class create enumerations
from Utils import getFromToCurrencies


class Side(enum.Enum):
    BUY = 1
    SELL = 2