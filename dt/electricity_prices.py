from typing import List

from dt.price import Price


class ElectricityPrices:
    prices: List[Price]
    prices_today: List[Price]
    prices_tomorrow: List[Price]
    max_price: float
    min_price: float

    def __init__(self):
        self.prices = []
