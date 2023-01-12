from typing import List

from dt.price import Price


class ElectricityPrices:
    prices: List[Price]
    max_price: float
    min_price: float

    def __init__(self):
        self.prices = []
